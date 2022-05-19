# Import flask dependencies
from operator import mod
from flask import Blueprint, request, jsonify, make_response, render_template
from flask_restful import Resource
from app import db, rest_api
from .models import Nowpos, DNowpos, PosSave
from .schema import NowposSchema, DNowposSchema, PosSaveSchema, PosSaveShortSchema, CarsSchema
import json
import decimal
from datetime import timedelta

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_api = Blueprint('api', __name__)

nowpos_schema = NowposSchema()
nowpoes_schema = NowposSchema(many=True)

dnowpos_schema = DNowposSchema()
dnowpoes_schema = DNowposSchema(many=True)

possave_schema = PosSaveSchema()
possaves_schema = PosSaveSchema(many=True)

possaves_short_schema = PosSaveShortSchema(many=True)


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)

@mod_api.route('/redoc')
def redoc():
    return render_template('redoc.html')

def carObj(car):
    return {
            "id": str(car.id),
            "事業所CD": str(car.事業所CD),
            "運転手": str(car.運転手),
            "日付": str(car.日付),
            "時間": str(car.時間),
            "location": {
                "Posx": str(car.Posx),
                "Posy": str(car.Posy)
            },
            "carstatus": [
                {
                    "rest": str(car.rest),
                    "battery": str(car.battery),
                    "status": str(car.status)
                }
            ]
        }


def nowpos_respond(obj):
    return {
        'id': str(obj.id),
        '事業所CD': str(obj.事業所CD),
        'rest': str(obj._isrest),
        '人数': str(obj._ninzu),
        '残人数': str(obj._ninzu_zan),
        'demandId': str(obj._demandid),
        'driver': str(obj._driver),
        'demand人数': str(obj._demand_ninzu),
        'demand残人数': str(obj._demand_zanninzu),
        '出発時間': str(obj._stime),
        '離接者情報': str(obj._risetsusya),
    }

class Action_index(Resource):
    def get(self):
        obj = {
            "事業所名": "高崎",
            "クラス名": "dnowpos",
            "バージョン": "1.1"
        }
        return obj, 200


class NowPosView(Resource):
    def get(self):
        binno = ''
        if request.args.get('id') is not None and request.args.get('id') != "":
            binno = request.args.get('id')

        jigyosyo = ''
        if request.args.get('事業所CD') is not None and request.args.get('事業所CD') != "":
            jigyosyo = request.args.get('事業所CD')

        queryset = Nowpos.query.filter((Nowpos.id == binno) | (Nowpos.事業所CD == jigyosyo))
        obj = {
            "cnt": queryset.count(),
            "cars": []
        }
        for car in queryset:
            obj['cars'].append(carObj(car))
        results = CarsSchema().dump(obj)

        if queryset.count() > 0:
            return results
        else:
            return [], 204

    def post(self):
        _isrest = ''
        _isrest = 'false'
        _rest_value = ''
        _update = False
        
        id = request.json['id']
        日付 = request.json['日付']
        時間 = request.json['時間']
        運転手 = request.json['運転手']
        Posx = request.json['Posx']
        Posy = request.json['Posy']
        rest = request.json['rest']
        battery = request.json['battery']
        binkubn_data = request.json['binkubun']
        imei = request.json['imei']
        deptime_data = request.json['deptime']
        出発時間 = request.json['出発時間']
        事業所CD = request.json['事業所CD']
        status = request.json['status']

        if request.args.get('id') is not None and request.args.get('id') != "":
            return jsonify({"message": "Id field is required!"})

        if request.args.get('事業所CD') is not None and request.args.get('事業所CD') != "":
            return jsonify({"message": "事業所CD field is required!"})

        if Nowpos.query.filter((Nowpos.id == id) & (Nowpos.事業所CD == 事業所CD)).count() > 0:
            return jsonify({"message": "This 事業所CD or id car already exist!"})
        
        if Nowpos.query.filter((Nowpos.id == id)).count() > 0:
            return jsonify({"message": "キーの値が既に存在します! primaryキーの値は重複できません。"})
        
        _rest_value = Nowpos.rest_data(id)        
        if _rest_value:
            _update = True
            _isrest = _rest_value[0]['rest']
            _issta = _rest_value[0]['status']
        
        #新設 2021/04/26
        _sdate_data   = 日付
        _binkubn_data = binkubn_data
        _deptime_data = deptime_data
        _ninzu = 0
        _ninzu_zan = 0
        #休み確認　20220110追加
        _userStatus = ""
        _demand_zanninzu = 0
        _demand_ninzu = 0
        _demandid = 0
        _driver = 0
        _stime = 0
        _risetsusya = 0
        _imei_data = imei
        _battery_data = battery
        
        #便の人数取得と降車されていない人数取得
        _ninzu_data = Nowpos.binninzu_data(id,_sdate_data,_binkubn_data,_deptime_data)
        if _ninzu_data:
            _ninzu = _ninzu_data[0]['CNT']
            _ninzu_zan = _ninzu_data[0]['CZ']            
            _userStatus = _ninzu_data[0]['userStatus']
            
        #demand人数取得
        _demandninzu_data = Nowpos.demandninzu_data(id,_sdate_data)
        if _demandninzu_data:
            #demand残人数取得
            _demand_zanninzu = _demandninzu_data[0]['CZ']
            _demand_ninzu = _demandninzu_data[0]['CNT']
            _demandid = _demandninzu_data[0]['demandId']
            _driver = _demandninzu_data[0]['driver']
            _stime = _demandninzu_data[0]['出発時間']

        queryset = Nowpos(id=id, 日付=日付, 時間=時間, 運転手=運転手, Posx=Posx, Posy=Posy, rest=rest, battery=battery, 出発時間=出発時間,
                          事業所CD=事業所CD, status=status, )
        db.session.add(queryset)
        db.session.commit()
        
        #20200903 ↓posSavsへの処理試験的追加        
        queryset1 = PosSave(id=id, 日付=日付, 時間=時間, lat=Posx, lng=Posy, imei=imei, rest=rest, battery=battery, 出発時間=出発時間,
                           事業所CD=事業所CD, status=status, )
        db.session.add(queryset1)
        db.session.commit()
        
        return {
            'id': str(id),
            '事業所CD': str(事業所CD),
            'rest': str(_isrest),
            '人数': str(_ninzu),
            '残人数': str(_ninzu_zan),
            'demandId': str(_demandid),
            'driver': str(_driver),
            'demand人数': str(_demand_ninzu),
            'demand残人数': str(_demand_zanninzu),
            '出発時間': str(_stime),
            '離接者情報': str(_risetsusya),
        }


class NowPosSingleView(Resource):
    
    def get(self, id):
        queryset = Nowpos.query.filter_by(id=id)
        if queryset.count() > 0:
            car = queryset.one()
            obj = {
                "cars": carObj(car)
            }
            return CarsSchema().dump(obj)
        return make_response(jsonify({"error": "Invalid credentials "}), 400)

    def put(self, id):
        _isrest = ''
        _isrest = 'false'
        _rest_value = ''
        日付 = request.json['日付']
        時間 = request.json['時間']
        運転手 = request.json['運転手']
        Posx = request.json['Posx']
        Posy = request.json['Posy']
        rest = request.json['rest']
        battery = request.json['battery']
        binkubn_data = request.json['binkubun']
        imei = request.json['imei']
        deptime_data = request.json['deptime']
        出発時間 = request.json['出発時間']
        事業所CD = request.json['事業所CD']
        status = request.json['status']

        queryset = Nowpos.query.get(id)
        if queryset is not None:
            queryset.id = id
            queryset.日付 = 日付
            queryset.時間 = 時間
            queryset.運転手 = 運転手
            queryset.Posx = Posx
            queryset.Posy = Posy
            queryset.rest = rest
            queryset.battery = battery
            queryset.出発時間 = 出発時間
            queryset.事業所CD = 事業所CD
            queryset.status = status
            
            _rest_value = Nowpos.rest_data(id)
            if _rest_value:                
                _isrest = _rest_value[0]['rest']
                _issta = _rest_value[0]['status']
            
            #新設 2021/04/26
            _sdate_data   = 日付
            _binkubn_data = binkubn_data
            _deptime_data = deptime_data
            _ninzu = 0
            _ninzu_zan = 0
            #休み確認　20220110追加            
            _demand_zanninzu = 0
            _demand_ninzu = 0
            _demandid = 0
            _driver = 0
            _stime = 0
            _risetsusya = 0
            _imei_data = imei
            _battery_data = battery
            
            #便の人数取得と降車されていない人数取得
            _ninzu_data = Nowpos.binninzu_data(id,_sdate_data,_binkubn_data,_deptime_data)
            if _ninzu_data:
                _ninzu = _ninzu_data[0]['CNT']
                _ninzu_zan = _ninzu_data[0]['CZ']            
                _userStatus = _ninzu_data[0]['userStatus']
                
            #demand人数取得
            _demandninzu_data = Nowpos.demandninzu_data(id,_sdate_data)
            if _demandninzu_data:
                #demand残人数取得
                _demand_zanninzu = _demandninzu_data[0]['CZ']
                _demand_ninzu = _demandninzu_data[0]['CNT']
                _demandid = _demandninzu_data[0]['demandId']
                _driver = _demandninzu_data[0]['driver']
                _stime = _demandninzu_data[0]['出発時間']
            
            db.session.commit()
            
            #[put]でもpossavsにinsertは可能
            queryset1 = PosSave(id=id, 日付=日付, 時間=時間, lat=Posx, lng=Posy, imei=imei, rest=rest, battery=battery, 出発時間=出発時間,
                           事業所CD=事業所CD, status=status, )
            db.session.add(queryset1) 
            db.session.commit()              
                
            return {
                'id': str(id),
                '事業所CD': str(事業所CD),
                'rest': str(_isrest),
                '人数': str(_ninzu),
                '残人数': str(_ninzu_zan),
                'demandId': str(_demandid),
                'driver': str(_driver),
                'demand人数': str(_demand_ninzu),
                'demand残人数': str(_demand_zanninzu),
                '出発時間': str(_stime),
                '離接者情報': str(_risetsusya),
            }
        return make_response(jsonify({"error": "Invalid credentials "}), 400)

    def delete(self, id):
        queryset = Nowpos.query.filter_by(id=id)
        if queryset.count() > 0:
            db.session.delete(queryset.one())
            db.session.commit()
            return make_response(jsonify({"message": "Deleted successfully!"}), 204)

        return make_response(jsonify({"error": "Invalid credentials "}), 400)


class JigyosyoView(Resource):
    def get(self):

        jigyosyo = ''
        if request.args.get('事業所CD') is not None and request.args.get('事業所CD') != "":
            jigyosyo = request.args.get('事業所CD')

        if jigyosyo != '':
            query_products = DNowpos.query.filter(DNowpos.事業所CD == jigyosyo)
            results = dnowpoes_schema.dump(query_products)
            if len(results) > 0:
                return results
            else:
                return [], 204
        else:
            query_products = DNowpos.query.all()
            results = dnowpoes_schema.dump(query_products)
            return results


class BinninzuView(Resource):
    def get(self):

        _id = ''
        if request.args.get('id') is not None and request.args.get('id') != "":
            _id = request.args.get('id')

        _date = ''
        if request.args.get('日付') is not None and request.args.get('日付') != "":
            _date = request.args.get('日付')

        _binkbn = ''
        if request.args.get('送迎区分') is not None and request.args.get('送迎区分') != "":
            _binkbn = request.args.get('送迎区分')

        _deptime = ''
        if request.args.get('出発時間') is not None and request.args.get('出発時間') != "":
            _deptime = request.args.get('出発時間')  

        
        query_products = DNowpos.find_data_binninzu(_id, _date, _binkbn, _deptime)
        
        if len(query_products) > 0:
            return {
                'CNT': str(query_products[0]['CNT']),
                'CZ': str(query_products[0]['CZ']),
                'userStatus': str(query_products[0]['userStatus'])
            }
        else:
            return [], 204


class PossavsDataView(Resource):
    def get(self):
        _date = ''
        if request.args.get('日付') is not None and request.args.get('日付') != "":
            _date = request.args.get('日付')

        # 時間
        _time = ''
        if request.args.get('時間') is not None and request.args.get('時間') != "":
            _time = request.args.get('時間')

        # savsId
        _savsid = ''
        if request.args.get('id') is not None and request.args.get('id') != "":
            _savsid = request.args.get('id')
            
        # 時間1(範囲指定)
        _time1 = ''
        if request.args.get('時間1') is not None and request.args.get('時間1') != "":
            _time1 = request.args.get('時間1')

        # 時間2(範囲指定)
        _time2 = ''
        if request.args.get('時間2') is not None and request.args.get('時間2') != "":
            _time2 = request.args.get('時間2')
        

        # 事業所CD
        _jigyosyo = ''
        if request.args.get('事業所CD') is not None and request.args.get('事業所CD') != "":
            _jigyosyo = request.args.get('事業所CD')        
        
        queryset = PosSave.find_data(_date, _time, _savsid, _jigyosyo, _time1, _time2)
        
        results = possaves_schema.dump(queryset)        
        results = json.dumps(results, cls = Encoder)
        results = json.loads(results)
        if len(results) > 0:
            resp = []
            for result in results:
                出発時間_delta = int(result['出発時間'])              
                出発時間 = timedelta(seconds=出発時間_delta)
                時間_delta = int(result['時間'])
                時間 = timedelta(seconds=時間_delta)
                res = {
                    "事業所CD": result['事業所CD'],
                    "id": result['id'],
                    "日付": result['日付'],
                    "時間": str(時間),
                    "lng": result['lng'],
                    "lat": result['lng'],
                    "出発時間": str(出発時間),    
                    "battery": result['battery'],                
                    "imei": result['imei'],
                    "rest": result['rest'],
                    "status": result['status']
                }
                resp.append(res)
            return resp
        else:
            return [], 204

    def post(self):
        id = request.json['id']
        日付 = request.json['日付']
        時間 = request.json['時間']
        lat = request.json['lat']
        lng = request.json['lng']
        rest = request.json['rest']
        imei = request.json['imei']
        battery = request.json['battery']
        出発時間 = request.json['出発時間']
        事業所CD = request.json['事業所CD']
        status = request.json['status']

        if PosSave.query.filter((PosSave.id == id) & (PosSave.事業所CD == 事業所CD)).count() > 0:
            return jsonify({"message": "This 事業所CD or id car already exist!"})

        queryset = PosSave(id=id, 日付=日付, 時間=時間, lat=lat, lng=lng, imei=imei, rest=rest, battery=battery, 出発時間=出発時間,
                           事業所CD=事業所CD, status=status, )

        db.session.add(queryset)
        db.session.commit()

        return nowpos_schema.dump(queryset), 201


class PossavsDataSingleView(Resource):

    def get(self, id,_date,_time):
        queryset = PosSave.query.filter((PosSave.id == id) & (PosSave.日付 ==_date) & (PosSave.時間 ==_time))
        if queryset.count() == 1:
            result = queryset.one()
            res = {
                "事業所CD": result.事業所CD,
                "id": result.id,
                "日付": str(result.日付),
                "時間": str(result.時間),
                "lng": result.lng,
                "lat": result.lat,
                "出発時間": str(result.出発時間),    
                "battery": result.battery,                
                "imei": result.imei,
                "rest": result.rest,
                "status": result.status
            }
            return res
        else:
            return [], 204
        

    def put(self, id,_date,_time):
        # _id = request.json['id']
        # 日付 = request.json['日付']
        # 時間 = request.json['時間']
        lat = request.json['lat']
        lng = request.json['lng']
        rest = request.json['rest']
        imei = request.json['imei']
        battery = request.json['battery']
        出発時間 = request.json['出発時間']
        事業所CD = request.json['事業所CD']
        status = request.json['status']

        queryset1 = PosSave.query.filter_by(id=id,日付=_date,時間=_time).first()
        if queryset1 is not None:
        #if queryset1.count() == 1:
            # queryset1.id = _id
            # queryset1.日付 = 日付
            # queryset1.時間 = 時間
            queryset1.lat = lat
            queryset1.lng = lng
            queryset1.rest = rest
            queryset1.imei = imei
            queryset1.battery = battery
            queryset1.出発時間 = 出発時間
            queryset1.事業所CD = 事業所CD
            queryset1.status = status
            
            db.session.commit()
            res = {
                "事業所CD": 事業所CD,
                "id": id,
                "日付": str(_date),
                "時間": str(_time),
                "lng": lng,
                "lat": lat,
                "出発時間": str(出発時間),    
                "battery": battery,                
                "imei": imei,
                "rest": rest,
                "status": status
            }
            return res

        return make_response(jsonify({"error": "無効なキー"}), 400)

    def delete(self, id,_date,_time):
        queryset = PosSave.query.filter((PosSave.id == id) & (PosSave.日付 ==_date) & (PosSave.時間 ==_time))
        if queryset.count() == 1:
            db.session.delete(queryset.one())
            db.session.commit()
            return make_response(jsonify({"message": "Deleted successfully!"}), 204)
        return make_response(jsonify({"error": "Invalid credentials "}), 400)


class PossavsView(Resource):

    def get(self):
        _date = ''
        if request.args.get('日付') is not None and request.args.get('日付') != "":
            _date = request.args.get('日付')

        # 時間
        _time = ''
        if request.args.get('時間') is not None and request.args.get('時間') != "":
            _time = request.args.get('時間')

        # lat
        _lat = ''
        if request.args.get('lat') is not None and request.args.get('lat') != "":
            _lat = request.args.get('lat')

        # lng
        _lng = ''
        if request.args.get('lng') is not None and request.args.get('lng') != "":
            _lng = request.args.get('lng')

        # _dist
        _dist = ''
        if request.args.get('dist') is not None and request.args.get('dist') != "":
            _dist = request.args.get('dist')

        # 事業所CD
        _jigyosyo = ''
        if request.args.get('事業所CD') is not None and request.args.get('事業所CD') != "":
            _jigyosyo = request.args.get('事業所CD')

        #queryset = PosSave.query.all()
        queryset = PosSave.find_pos(_date, _time, _lat, _lng, _dist)
           
        results = possaves_short_schema.dump(queryset)        
        results = json.dumps(results, cls = Encoder)
        results = json.loads(results)
        if len(results) > 0:
            resp = []
            for result in results:
                
                時間_delta = int(result['時間'])
                時間 = timedelta(seconds=時間_delta)
                res = {                    
                    "事業所CD": result['事業所CD'],
                    "id": result['id'],
                    "日付": result['日付'],
                    "時間": str(時間),
                    "lng": result['lng'],
                    "lat": result['lng'],
                    "rest": result['rest']
                    
                }
                resp.append(res)
            return resp
        else:
            return [], 204

rest_api.add_resource(Action_index, '/action-index/')
rest_api.add_resource(NowPosView, '/nowpos-data/')

rest_api.add_resource(NowPosSingleView, '/nowpos-data/<id>/')

rest_api.add_resource(JigyosyoView, '/jigyosyo-data/')
rest_api.add_resource(BinninzuView, '/binninzu-data/')


rest_api.add_resource(PossavsView, '/possavs/')
rest_api.add_resource(PossavsDataView, '/possavs-data/')
rest_api.add_resource(PossavsDataSingleView, '/possavs-data/<int:id>/<string:_date>/<string:_time>')
