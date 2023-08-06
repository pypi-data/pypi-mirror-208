import datetime
import logging
import time
import traceback
from _thread import allocate_lock
import tzlocal
import wsqluse.wsqluse
from pytz import timezone
import json
import random
import requests
from ar_external_sys_worker import mixins
import uuid
import socket


class DataWorker(mixins.Logger, mixins.ExSys, mixins.AuthMe,
                 mixins.DbAuthInfoGetter):
    working_link = None

    def is_valid_uuid(self, val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    def get_send_data(self):
        return True

    def format_send_data(self, data, *args, **kwargs):
        return data

    def get_local_id(self, data):
        return data['ex_id']

    def get_and_send_data(self):
        data = self.get_send_data()
        return self.send_data(data)

    def post_data(self, headers, link, data):
        return requests.post(url=link,
                             data=data,
                             headers=headers)

    def get_data(self, headers, link, data=None, params=None):
        return requests.get(url=link, data=data, headers=headers,
                            params=params)

    def send_data(self, data):
        local_data_id = self.get_local_id(data)
        print(f"\nSENDING: id #{local_data_id}")
        data_frmt = self.format_send_data(data)
        log_id = self.log_ex_sys_sent(local_data_id)
        self.log_ex_sys_data(data_frmt, log_id)
        act_send_response = self.post_data(headers=self.headers,
                                           link=self.get_full_endpoint(
                                               self.link_create_act),
                                           data=data_frmt)
        ex_sys_data_id = self.get_ex_sys_id_from_response(act_send_response)
        print(f"\nSEND RESULT: ex_id #{ex_sys_data_id}")
        self.log_ex_sys_get(ex_sys_data_id, log_id)
        return act_send_response

    def get_ex_sys_id_from_response(self, response):
        return response


class ActsWorker(DataWorker, mixins.ActWorkerMixin, mixins.ActsSQLCommands):
    table_name = 'records'
    table_id = 1
    act_id_from_response = None

    def __init__(self, sql_shell, trash_cats=None, time_start=None,
                 acts_limit=4, login=None, password=None, auto_auth=True,
                 *args, **kwargs):
        self.sql_shell = sql_shell
        self.limit = acts_limit
        if trash_cats is None:
            trash_cats = ['ТКО', 'ПО']
        self.trash_cats_to_send = tuple(trash_cats)
        if len(self.trash_cats_to_send) == 1:
            self.trash_cats_to_send = str(self.trash_cats_to_send).replace(',',
                                                                           '')
        self.time_start = time_start
        self.login = login
        self.password = password
        self.mutex = allocate_lock()
        if auto_auth:
            self.auth()

    def auth(self):
        self.set_headers(self.get_headers())

    def send_unsend_acts(self, record_id=None, limit=None):
        self.mutex.acquire()
        try:
            data = self.get_unsend_acts(record_id=record_id, limit=limit)
            if not data:
                self.mutex.release()
                return {'error': 'no acts to send'}
            for act in data:
                self.send_data(act)
        except:
            print(traceback.format_exc())
        finally:
            if self.mutex.locked():
                self.mutex.release()

    def get_ex_sys_id_from_response(self, response):
        response = response.json()
        if 'error' in response:
            return response['error']
        return response[self.act_id_from_response]

    def get_photo_path(self, record_id, photo_type):
        command = "SELECT p.path FROM photos p " \
                  "INNER JOIN record_photos rp ON (p.id = rp.photo_id) " \
                  "WHERE p.photo_type={} and rp.record_id={} LIMIT 1".format(
            photo_type,
            record_id)
        response = self.sql_shell.try_execute_get(command)
        if response:
            return response[0][0]

    @wsqluse.wsqluse.getTableDictStripper
    def get_photo_types(self, sql_shell):
        return sql_shell.get_table_dict(
            "SELECT id, name FROM photo_types"
        )

    def get_send_data(self):
        return self.get_one_unsend_act()


class ASUActsWorker(mixins.AsuMixin, ActsWorker,
                    mixins.SignallPhotoEncoderMixin):
    def __init__(self, sql_shell, trash_cats_list, time_start, acts_limit=3,
                 login=None, password=None):
        super().__init__(sql_shell=sql_shell, trash_cats=trash_cats_list,
                         time_start=time_start, acts_limit=acts_limit,
                         login=login, password=password)
        self.working_link = self.get_full_endpoint(self.link_create_act)
        self.fetch_asu_auto_id_url = self.get_full_endpoint(
            "/extapi/v2/transport/?number={}")
        self.get_route_id_url = self.get_full_endpoint(
            "/extapi/v2/trip/"
        )
        self.asu_polygon_name = None
        self.get_platform_url = self.get_full_endpoint("/extapi/v2/platform")

    def format_file_before_logging(self, data):
        data = json.loads(data)
        return str(data).replace("'", '"')

    def send_unsend_acts(self, record_id=None, limit=None):
        data = self.get_unsend_acts(record_id=record_id, limit=limit)
        if not data:
            return {'error': 'no acts to send'}
        for act in data:
            response = self.send_data(act)
            asu_act_id = response.json()['id']
            photo_in = self.get_photo_path(act['ex_id'], 1)
            photo_out = self.get_photo_path(act['ex_id'], 2)
            photo_in = self.get_photo_data(photo_in)
            self.upload_photo(photo_in,
                              self.get_full_endpoint(
                                  "/extapi/v2/landfill-fact/{}/photos-arrival/".format(
                                      asu_act_id)))
            photo_out = self.get_photo_data(photo_out)
            self.upload_photo(photo_out,
                              self.get_full_endpoint(
                                  "/extapi/v2/landfill-fact/{}/photos-departure/".format(
                                      asu_act_id)
                              ))

    def upload_photo(self, photoobj, endpoint):
        data = {"file": photoobj}
        data = json.dumps(data)
        response = requests.post(endpoint, data=data, headers=self.headers)
        return response

    def send_auth_data(self, endpoint, auth_data, *args, **kwargs):
        auth_data_json = json.dumps(auth_data)
        return requests.post(endpoint, data=auth_data_json,
                             headers={"Content-Type": "application/json"},
                             *args, **kwargs)

    def set_headers(self, headers):
        headers.update({"Content-Type": "application/json"})
        self.headers = headers

    def get_ex_sys_id_from_response(self, response):
        return response.json()['id']

    def extract_token(self, auth_response):
        token = super().extract_token(auth_response)
        return f"Token {token}"

    def fetch_asu_auto_name(self, car_number):
        response = self.get_data(headers=self.headers,
                                 link=self.fetch_asu_auto_id_url.format(
                                     car_number
                                 ),
                                 data=None)
        try:
            car_name = response.json()['results'][0]['name']
        except IndexError:
            car_name = "No car found in ASU"
        return car_name

    def get_route_info(self, car_number, timestamp):
        auto_id = self.fetch_asu_auto_id(car_number)
        if auto_id == 9999:
            return {'error': 'Auto is not found in ASU'}
        try:
            route_id = self.fetch_asu_route_id(auto_id=auto_id,
                                               timestamp=timestamp)
        except IndexError:
            return {'error': "Route is not found in ASU"}
        route_info = self.fetch_route_info(route_id)
        containers_info = self.get_containers_info(route_info)
        containers_info.update({'route_id': route_id})
        return containers_info

    def fetch_route_info(self, route_id):
        url = f"{self.get_route_id_url}{route_id}/"
        response = self.get_data(headers=self.headers,
                                 link=url,
                                 params={'is_deleted': False})
        return response.json()

    def get_containers_info(self, route_info):
        response = {}
        print(route_info)
        response['containers_plan'] = route_info['_supplement_sum']['plan'][
            'containers_count']
        response['containers_fact'] = route_info['_supplement_sum']['report'][
            'containers_count']
        return response

    def make_db_record_about_route(self, car_number, date, record_id):
        try:
            routes_info = self.get_route_info(
                car_number=car_number,
                timestamp=datetime.datetime.today().strftime('%d.%m.%Y'))
            if 'error' in routes_info:
                route_id = routes_info['error']
                containers_plan = 0
                containers_fact = 0
            else:
                route_id = routes_info['route_id']
                containers_plan = routes_info['containers_plan']
                containers_fact = routes_info['containers_fact']
            self.create_route_info_record(
                record_id=record_id,
                route_num=route_id,
                containers_plan=containers_plan,
                containers_fact=containers_fact)
        except:
            print(traceback.format_exc())
            logging.error(traceback.format_exc())

    def create_route_info_record(self, record_id, route_num,
                                 containers_plan,
                                 containers_fact):
        command = "INSERT INTO records_routes_info (record_id, route_num, " \
                  "containers_plan, containers_fact) VALUES ({}, '{}', '{}'," \
                  "'{}')".format(record_id, route_num, containers_plan,
                                 containers_fact)
        return self.sql_shell.try_execute(command)

    def fetch_asu_route_id(self, auto_id, timestamp):
        response = self.get_data(headers=self.headers,
                                 link=self.get_route_id_url,
                                 params={'transport': auto_id,
                                         'trip_group__date': timestamp,
                                         'is_deleted': False})
        return response.json()['results'][0]['id']

    def fetch_asu_auto_id(self, car_number):
        print("HEADERS", self.headers)
        response = self.get_data(headers=self.headers,
                                 link=self.fetch_asu_auto_id_url.format(
                                     car_number
                                 ),
                                 data=None)
        try:
            print(response.json())
            car_id = response.json()['results'][0]['id']
        except IndexError:
            car_id = 9999
        return car_id

    def get_platform_weekdays(self, platform_id):
        response = self.get_data(headers=self.headers,
                                 link=self.get_platform_url,
                                 params={"id": platform_id})
        return response

    def format_send_data(self, act, photo_in=None, photo_out=None):
        asu_auto_id = self.fetch_asu_auto_id(act['car_number'])
        if not act['rfid']: act['rfid'] = 'None'
        data = {
            "ext_id_landfill_weight": self.get_db_value('asu_poligon_name'),
            "ext_id_transport_weight": act["car_number"],
            "ext_id": str(act["ex_id"]),
            "time_arrival": self.format_date_for_asu(act["time_in"]),
            "time_departure": self.format_date_for_asu(act["time_out"]),
            "transport_arrival_weight": act["gross"],
            "transport_departure_weight": act["tare"],
            "allow_weight_fault": 50,
            "rfid": act['rfid'],
            "transport": asu_auto_id,
            "transport_name": act["car_number"],
            "transport_number": act["car_number"],
            'comment': ''
        }
        act_json = json.dumps(data)
        return act_json

    def format_date_for_asu(self, date):
        date = self.set_current_localzone(date)
        date = self.convert_time_to_msk(date, new_timezone='GMT')
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        return date

    def set_current_localzone(self, date):
        date = date.replace(tzinfo=None)
        current_localzone = tzlocal.get_localzone()
        date = current_localzone.localize(date)
        return date

    def convert_time_to_msk(self, date, new_timezone, *args, **kwargs):
        date = date.astimezone(timezone(new_timezone))
        return date


class SignallActWorker(mixins.SignallMixin, ActsWorker,
                       mixins.SignallPhotoEncoderMixin,
                       mixins.SignallGetCarriersPO):
    def __init__(self, sql_shell, trash_cats_list, time_start, acts_limit=5,
                 login=None, password=None, auto_auth=True, mutex=None):
        super().__init__(sql_shell=sql_shell, trash_cats=trash_cats_list,
                         time_start=time_start, acts_limit=acts_limit,
                         login=login, password=password, auto_auth=auto_auth)
        self.get_carriers_po_link = self.get_full_endpoint(
            self.link_get_po_links)
        self.act_id_from_response = 'act_id'
        if mutex:
            self.mutex = mutex

    def format_file_before_logging(self, data):
        data = json.loads(data)
        data.pop('photos')
        return str(data).replace("'", '"')

    def format_alerts(self, alerts):
        if not alerts:
            return []
        res = alerts.split('&&')
        return res[:-1]

    def format_send_data_old(self, act, photo_in=None, photo_out=None):
        act.pop('polygon_id')
        act.pop('rfid')
        alerts_string = act.pop('alerts')
        # alerts = self.get_alerts(act['ex_id'])
        act['platform_type'] = act.pop('pol_object')
        act_number = act.pop('act_number')
        package = act.pop('package_name')
        act_number = {'number': act_number,
                      'package': package}
        act['operator_comments'] = {'gross_comm': act.pop('gross_comm'),
                                    'tare_comm': act.pop('tare_comm'),
                                    'add_comm': act.pop('add_comm'),
                                    'changing_comm': act.pop(
                                        'changing_comm'),
                                    'closing_comm': act.pop(
                                        'closing_comm')}
        act['alerts'] = self.format_alerts(alerts_string)
        act['photo_in'] = self.get_photo_path(act['ex_id'], 1)
        act['photo_out'] = self.get_photo_path(act['ex_id'], 2)
        if act['photo_in']:
            photo_in = self.get_photo_data(act['photo_in'])
        if act['photo_out']:
            photo_out = self.get_photo_data(act['photo_out'])
        act_json = self.get_json(car_number=act['car_number'],
                                 ex_id=act['ex_id'],
                                 gross=act['gross'],
                                 tare=act['tare'],
                                 cargo=act['cargo'],
                                 time_in=act['time_in'].strftime(
                                     '%Y-%m-%d %H:%M:%S'),
                                 time_out=act['time_out'].strftime(
                                     '%Y-%m-%d %H:%M:%S'),
                                 alerts=act['alerts'], carrier=act['carrier'],
                                 trash_cat=act['trash_cat'],
                                 trash_type=act['trash_type'],
                                 operator_comments=act['operator_comments'],
                                 photo_in=photo_in,
                                 photo_out=photo_out,
                                 containers_plan=act['containers_plan'],
                                 containers_fact=act['containers_fact'],
                                 route_num=act["route_num"],
                                 platform_type=act["platform_type"],
                                 act_number=act_number)
        return act_json

    def get_photos(self, record_id):
        photo_types = self.get_photo_types(self.sql_shell)
        new_dict = {}
        for photo_type in photo_types:
            photo_path = self.get_photo_path(record_id, photo_type["id"])
            if photo_path:
                photo_obj = self.get_photo_data(photo_path)
                new_dict[photo_type['name']] = photo_obj
        return new_dict


    def format_send_data(self, act, photo_in=None, photo_out=None):
        data = {
            "car_number": act['car_number'],
            "ex_id": act['ex_id'],
            "gross": act['gross'],
            "tare": act['tare'],
            "cargo": act['cargo'],
            "time_in": act['time_in'].strftime(
                                     '%Y-%m-%d %H:%M:%S'),
            "time_out": act['time_out'].strftime(
                                     '%Y-%m-%d %H:%M:%S'),
            "alerts": self.format_alerts(act['alerts']),
            "carrier": {"inn": act['carrier_inn'],
                        "kpp": act['carrier_kpp']},
            "client": {"inn": act['client_inn'],
                        "kpp": act['client_kpp']},
            "trash_cat": act['trash_cat'],
            "trash_type": act['trash_type'],
            "operator_comments": {'gross_comm': act['gross_comm'],
                                    'tare_comm': act['tare_comm'],
                                    'add_comm': act['add_comm'],
                                    'changing_comm': act['changing_comm'],
                                    'closing_comm': act['closing_comm'],
                                    'single_comm': act['single_comm']},
            "photos": self.get_photos(act['ex_id']),
            "containers_plan": act['containers_plan'],
            'containers_fact': act['containers_fact'],
            "route_num": act["route_num"],
            'platform_type': act['pol_object'],
            "act_number": {'number': act['act_number'],
                           'package': act['package_name']},
        }
        act_json = json.dumps(data)
        return act_json


class SignAllActsWorkerToken(mixins.TokenAuth, SignallActWorker,
                             mixins.TokenDBAuth, mixins.SignallActDBDeletter):
    def __init__(self, sql_shell, trash_cats_list, time_start, platform_id,
                 acts_limit=5, gravity_ip=None, gravity_port=8080, test=False,
                 mutex=None):
        super().__init__(sql_shell, trash_cats_list, time_start, acts_limit,
                         auto_auth=False, mutex=mutex)
        self.platform_id = platform_id
        self.gravity_ip = gravity_ip
        if not self.gravity_ip:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.gravity_ip = s.getsockname()[0]
        self.gravity_port = gravity_port
        platform_info = self.get_platform_info()[0]
        self.inn, self.kpp = platform_info['inn'], platform_info['kpp']
        if test:
            self.link_host = 'https://signalltestdev.qodex.tech'

    def resend_unget_acts(self):
        print("Resending acts")
        self.mutex.acquire()
        unsend_acts = self.get_unget_by_signall_acts()
        if not unsend_acts:
            self.mutex.release()
            return
        for act in unsend_acts:
            self.delete_act_from_send_reports(act['local_id'])
        self.send_unsend_acts(limit=len(unsend_acts))
        self.mutex.release()

    @wsqluse.wsqluse.getTableDictStripper
    def get_platform_info(self):
        return self.sql_shell.get_table_dict(
            command=f"SELECT inn, kpp FROM duo_pol_owners "
                    f"WHERE id={self.platform_id}")

    def get_acts_all_command(self):
        response = super(SignAllActsWorkerToken, self).get_acts_all_command()
        response += f" AND dro.owner={self.platform_id}"
        return response

    def get_token(self):
        token = self.get_token_db()
        if not token:
            response = self.get_token_url(
                self.get_full_endpoint(self.link_get_token))
            if not response.status_code == 200:
                return {'error': response.status_code}
            response_json = response.json()
            if 'error' in response_json:
                return response_json
            token = response_json['token']
            self.set_token_db(token)
        return token


class ASURoutesWorker(mixins.AsuMixin, DataWorker):
    def __init__(self, sql_shell, asu_login, asu_password, **kwargs):
        self.sql_shell = sql_shell
        self.login = asu_login
        self.password = asu_password
        self.headers = self.get_headers()

    def send_auth_data(self, endpoint, auth_data, *args, **kwargs):
        auth_data_json = json.dumps(auth_data)
        return requests.post(endpoint, data=auth_data_json,
                             headers={"Content-Type": "application/json"},
                             *args, **kwargs)

    def set_headers(self, headers):
        headers.update({"Content-Type": "application/json"})
        self.headers = headers

    def get_ex_sys_id_from_response(self, response):
        return response.json()['id']

    def extract_token(self, auth_response):
        token = super().extract_token(auth_response)
        return f"Token {token}"


class SignallActReuploder(mixins.SignallMixin, DataWorker,
                          mixins.SignallActDeletter,
                          mixins.SignallActDBDeletter):
    def __init__(self, sql_shell, login=None, password=None, test=False,
                 **kwargs):
        self.sql_shell = sql_shell
        self.login = login
        self.password = password
        if test:
            self.link_host = 'https://signalltestdev.qodex.tech'
        self.headers = self.get_headers()
        self.working_link = self.get_full_endpoint(self.del_act_url)

    def work(self, act_number):
        print(f"DEL ACT #{act_number}")
        response = self.delete_act(act_number)
        print(f"SIGNALL RESULT:{response.json()}")
        response = self.delete_act_from_send_reports(act_number)
        print(f"DB RESULT:{response}")

    def delete_unsend_acts(self):
        unsend_acts = self.get_unsend_acts()
        for act in unsend_acts:
            self.delete_act_from_send_reports(act['local_id'])

class SignallActUpdater(mixins.SignallMixin, DataWorker,
                        mixins.ExSysActIdExtractor,
                        mixins.SignallActUpdater,
                        mixins.SignallActDBDeletter):
    def __init__(self, sql_shell, login=None, password=None, test=False,
                 **kwargs):
        self.sql_shell = sql_shell
        self.login = login
        self.password = password
        self.headers = self.get_headers()
        if test:
            self.link_host = "https://signalltestdev.qodex.tech"
        self.working_link = self.get_full_endpoint(
            '/v1/gravity/update_act/{}')

    def work(self, record_id, car_number, transporter_inn, trash_cat,
             trash_type, comment):
        signal_id = self.extract_act_ex_id(record_id)
        if not signal_id:
            return
        if signal_id.strip() == 'this carrier was not found':
            self.delete_act_from_send_reports(record_id)
            return {'error': {f'Act has not been delivered cos {signal_id}. '
                              f'Deleted from log...'}}
        if not self.is_valid_uuid(signal_id):
            return {'error': f'act not found in signall_id ({signal_id})'}
        return self.update_act(
            signall_id=signal_id,
            car_number=car_number,
            transporter_inn=transporter_inn,
            trash_cat=trash_cat,
            trash_type=trash_type,
            comment=comment)


class SignallAutoGetter(mixins.SignallMixin, DataWorker,
                        mixins.SignAllCarsGetter):
    def __init__(self, sql_shell, ar_ip, **kwargs):
        self.sql_shell = sql_shell
        self.headers = self.get_headers()
        self.working_link = self.get_full_endpoint(
            '/v1/gravity/car')
        self.ar_ip = ar_ip

    def insert_car_to_gravity(self, car_number, ident_number, ident_type,
                              auto_chars):
        return requests.post(url=f'{self.ar_ip}:8080/add_auto',
                             params=
                             {'car_number': car_number,
                              'ident_number': ident_number,
                              'ident_type': ident_type,
                              'auto_chars': auto_chars})


class SignallClientsGetter(mixins.SignallMixin, DataWorker,
                           mixins.SignAllCarsGetter):
    def __init__(self, sql_shell, ar_ip, login, password, **kwargs):
        self.sql_shell = sql_shell
        self.login = login
        self.password = password
        self.headers = self.get_headers()
        self.working_link = self.get_full_endpoint(
            '/v1/gravity/transporter')
        self.ar_ip = ar_ip

    def import_clients(self):
        resp = self.get_cars()
        for client in resp['transporters']:
            self.insert_client_to_gravity(name=client['name'],
                                          inn=client['inn'],
                                          kpp=client['kpp'],
                                          push_to_cm=False)
            self.make_client_tko_carrier(inn=client['inn'],
                                         push_to_cm=False)

    def insert_client_to_gravity(self, name, inn, kpp, push_to_cm):
        return requests.post(url=f'{self.ar_ip}:8080/add_client',
                             params=
                             {'name': name,
                              'inn': inn,
                              'kpp': kpp,
                              'push_to_cm': push_to_cm,
                              })

    def make_client_tko_carrier(self, inn, push_to_cm):
        return requests.post(url=f'{self.ar_ip}:8080/make_client_tko_carrier',
                             params=
                             {
                                 'inn': inn,
                                 'push_to_cm': push_to_cm
                             })
