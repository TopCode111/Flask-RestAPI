# Import flask dependencies
from flask import Blueprint, request, jsonify, make_response, render_template
from flask_restful import Resource
from app import db, rest_api
from .models import Nowpos, DNowpos, PosSave
from .schema import NowposSchema, DNowposSchema, PosSaveSchema, PosSaveShortSchema, CarsSchema

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_api = Blueprint('api', __name__)

nowpos_schema = NowposSchema()
nowpoes_schema = NowposSchema(many=True)

dnowpos_schema = DNowposSchema()
dnowpoes_schema = DNowposSchema(many=True)

possave_schema = PosSaveSchema()
possaves_schema = PosSaveSchema(many=True)

possaves_short_schema = PosSaveShortSchema(many=True)


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
        id = request.json['id']
        日付 = request.json['日付']
        時間 = request.json['時間']
        運転手 = request.json['運転手']
        Posx = request.json['Posx']
        Posy = request.json['Posy']
        rest = request.json['rest']
        battery = request.json['battery']
        出発時間 = request.json['出発時間']
        事業所CD = request.json['事業所CD']
        status = request.json['status']

        if request.args.get('id') is not None and request.args.get('id') != "":
            return jsonify({"message": "Id field is required!"})

        if request.args.get('事業所CD') is not None and request.args.get('事業所CD') != "":
            return jsonify({"message": "事業所CD field is required!"})

        if Nowpos.query.filter((Nowpos.id == id) | (Nowpos.事業所CD == 事業所CD)).count() > 0:
            return jsonify({"message": "This 事業所CD or id car already exist!"})

        queryset = Nowpos(id=id, 日付=日付, 時間=時間, 運転手=運転手, Posx=Posx, Posy=Posy, rest=rest, battery=battery, 出発時間=出発時間,
                          事業所CD=事業所CD, status=status, )
        db.session.add(queryset)
        db.session.commit()

        return nowpos_schema.dump(queryset), 201


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
        日付 = request.json['日付']
        時間 = request.json['時間']
        運転手 = request.json['運転手']
        Posx = request.json['Posx']
        Posy = request.json['Posy']
        rest = request.json['rest']
        battery = request.json['battery']
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
            db.session.commit()
            car = queryset
            obj = {
                "cars": carObj(car)
            }
            return CarsSchema().dump(obj)
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

        query_products = DNowpos.query.filter(Nowpos.事業所CD == jigyosyo)
        results = dnowpoes_schema.dump(query_products)
        if len(results) > 0:
            return results
        else:
            return [], 204


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

        query_products = DNowpos.query.all()
        #query_products = DNowpos.find_data_binninzu(id, _date, _binkbn, _deptime)

        results = dnowpoes_schema.dump(query_products)
        if len(results) > 0:
            return results
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
            _date = request.args.get('時間')

        # 時間1(範囲指定)
        _time1 = ''
        if request.args.get('時間1') is not None and request.args.get('時間1') != "":
            _date = request.args.get('時間1')

        # 時間2(範囲指定)
        _time2 = ''
        if request.args.get('時間2') is not None and request.args.get('時間2') != "":
            _date = request.args.get('時間2')

        # savsId
        _savsid = ''
        if request.args.get('id') is not None and request.args.get('id') != "":
            _date = request.args.get('id')

        # 事業所CD
        _jigyosyo = ''
        if request.args.get('事業所CD') is not None and request.args.get('事業所CD') != "":
            _date = request.args.get('事業所CD')

        queryset = PosSave.query.filter((PosSave.事業所CD == _jigyosyo) | (PosSave.id == _savsid) | (PosSave.時間 >= _time) | (PosSave.日付 == _date))
        results = possaves_schema.dump(queryset)

        if len(results) > 0:
            return results
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

        if PosSave.query.filter((PosSave.id == id) | (PosSave.事業所CD == 事業所CD)).count() > 0:
            return jsonify({"message": "This 事業所CD or id car already exist!"})

        queryset = PosSave(id=id, 日付=日付, 時間=時間, lat=lat, lng=lng, imei=imei, rest=rest, battery=battery, 出発時間=出発時間,
                           事業所CD=事業所CD, status=status, )

        db.session.add(queryset)
        db.session.commit()

        return nowpos_schema.dump(queryset), 201


class PossavsDataSingleView(Resource):

    def get(self, id):
        queryset = PosSave.query.filter_by(id=id)
        if queryset.count() > 0:
            return possave_schema.dump(queryset.one())
        return make_response(jsonify({"error": "Invalid credentials "}), 400)

    def put(self, id):
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

        queryset = PosSave.query.get(id)
        if queryset is not None:
            queryset.id = id
            queryset.日付 = 日付
            queryset.時間 = 時間
            queryset.lat = lat
            queryset.lng = lng
            queryset.rest = rest
            queryset.imei = imei
            queryset.battery = battery
            queryset.出発時間 = 出発時間
            queryset.事業所CD = 事業所CD
            queryset.status = status
            db.session.commit()
            return possave_schema.dump(queryset)

        return make_response(jsonify({"error": "Invalid credentials "}), 400)

    def delete(self, id):
        queryset = PosSave.query.filter_by(id=id)
        if queryset.count() > 0:
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
            _lng = request.args.get('dist')

        # 事業所CD
        _jigyosyo = ''
        if request.args.get('事業所CD') is not None and request.args.get('事業所CD') != "":
            _jigyosyo = request.args.get('事業所CD')

        queryset = PosSave.query.filter(
            (PosSave.日付 == _date) & (PosSave.時間 >= _time) & (PosSave.lat == _lat) & (PosSave.lng == _lng) & (
                    PosSave.事業所CD == _jigyosyo))
        results = possaves_short_schema.dump(queryset)

        if len(results) > 0:
            return results
        else:
            return [], 204


rest_api.add_resource(Action_index, '/action-index/')
rest_api.add_resource(NowPosView, '/nowpos-data/')

rest_api.add_resource(NowPosSingleView, '/nowpos-data/<id>/')

rest_api.add_resource(JigyosyoView, '/jigyosyo-data/')
rest_api.add_resource(BinninzuView, '/binninzu-data/')


rest_api.add_resource(PossavsView, '/possavs/')
rest_api.add_resource(PossavsDataView, '/possavs-data/')
rest_api.add_resource(PossavsDataSingleView, '/possavs-data/<id>/')
