from app import db
import sqlalchemy as sa

class Nowpos(db.Model):
    __tablename__ = "NowPos"

    id = db.Column(db.Integer, primary_key=True)
    日付 = db.Column(db.Date)
    時間 = db.Column(db.Time)
    運転手 = db.Column(db.String(20))
    Posx = db.Column(db.Float)
    Posy = db.Column(db.Float)
    rest = db.Column(db.String(1))
    battery = db.Column(db.String(3))
    出発時間 = db.Column(db.Time)
    事業所CD = db.Column(db.String(4))
    status = db.Column(db.String(20))
    
    @staticmethod
    def rest_data(id=None):
        with db.engine.begin() as conn:
            sql = ""
            sql += "select rest,status"
            sql += " FROM NowPos"
            sql += " WHERE id='" + str(id) + "'"
            resultset = conn.execute(sql)
            results_as_dict = resultset.mappings().all()
            return results_as_dict
        
    @staticmethod
    def binninzu_data(id, sdate, binkubun, deptime):
        with db.engine.begin() as conn:
            sql = "";
            sql += "select count(*) as CNT,sum(if(c.降車時刻 is not null,0,1)) as CZ"
            sql += " ,if(sum(if(((carStatus is null)and(userStatus='休み')),'1','0'))>0,'休み',null) as userStatus"
            sql += " from mergedata a"
            sql += " left join bindatad c on ((a.日付=c.日付)and(a.送迎区分=c.送迎区分)and(a.利用者番号=c.利用者番号))"
            sql += " where a.日付='" + str(sdate) + "'"
            sql += " and a.carId='" + str(id) + "'"
            sql += " and a.出発時間='" + str(deptime) + "'"
            sql += " and not ((Left(a.利用者番号,1)='A')or(Left(a.利用者番号,1)='E'))"
            sql += " and a.休=0"
            
            resultset = conn.execute(sql)
            results_as_dict = resultset.mappings().all()
            return results_as_dict
    
    @staticmethod
    def demandninzu_data(id, sdate):
        with db.engine.begin() as conn:
            sql = ""
            sql += " select v.demandId,v.driver,v.出発時間,CNT,SUM(CZ) as CZ from ("
            sql += " (select a1.demandId,a1.driver,a1.出発時間,(a1.人数 + a1.gate) as CNT,if(a1.demandId is not null,1,0) - if(c1.乗車時刻 is not null,1,0) as CZ from demandDataV a1"
            sql += " left join bindatad c1 on ((a1.日付=c1.日付)and(concat('J',a1.demandId,'1')=c1.利用者番号))"
            sql += " LEFT JOIN bookmark k1 ON (a1.pickUpId=k1.bid)"
            sql += " where ((a1.status='PICKING_UP')or(a1.status='BOARDING'))"
            sql += " AND a1.日付='" + str(sdate) + "'"
            sql += " AND a1.savId='" + str(id) + "'"
            sql += " )"
            sql += " union all"
            sql += " (select a2.demandId,a2.driver,a2.出発時間,(a2.人数 + a2.gate) as CNT,if(a2.demandId is not null,1,0) - if(c2.乗車時刻 is not null,1,0) as CZ from demandDataV a2"
            sql += " left join bindatad c2 on ((a2.日付=c2.日付)and(concat('J',a2.demandId,'2')=c2.利用者番号))"
            sql += " LEFT JOIN bookmark k2 ON (a2.dropOffId=k2.bid)"
            sql += "  where ((a2.status='PICKING_UP')or(a2.status='BOARDING'))"
            sql += " AND a2.日付='" + str(sdate) + "'"
            sql += " AND a2.savId='" + str(id) + "'"
            sql += " )"
            sql += " ) as v"
            
            resultset = conn.execute(sql)
            results_as_dict = resultset.mappings().all()
            return results_as_dict
    

class DNowpos(db.Model):
    __tablename__ = "事業所"

    事業所CD = db.Column(db.String(4), primary_key=True)
    事業所番号 = db.Column(db.String(6))
    事業所名 = db.Column(db.String(20))
    フリガナ = db.Column(db.String(30))
    memo = db.Column(db.String(30))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    service_range = db.Column(db.Integer)

    @staticmethod
    def find_data_binninzu(id, date, binkbn, deptime):
        from app import db
        with db.engine.begin() as conn:
            sql = ""
            sql += "select count(*) as CNT,sum(if(c.降車時刻 is not null,0,1)) as CZ"
            sql += " ,if(sum(if(((carStatus is null)and(userStatus is not null)),'1','0'))>0,'休み',null) as userStatus"
            sql += " from mergedata a"
            sql += " left join bindatad c on ((a.日付=c.日付)and(a.送迎区分=c.送迎区分)and(a.事業所CD=c.事業所CD)and(a.利用者番号=c.利用者番号))"
            sql += " where a.休=0"

            if date != '':
                sql += " and a.日付='" + str(date) + "'"

            if id != '':
                sql += " and a.carId='" + str(id) + "'"
            
            if deptime:
                sql += " and a.出発時間='" + str(deptime) + "'"

            sql += " and ((a.利用者番号 is not null)or(Left(a.利用者番号,1)='A')or(Left(a.利用者番号,1)='E'))"

            resultset = conn.execute(sql)
            results_as_dict = resultset.mappings().all()
            return results_as_dict
    
    

class PosSave(db.Model):
    __tablename__ = "posSavs"

    id = db.Column(db.String(3), primary_key=True)
    日付 = db.Column(db.Date, primary_key=True)
    時間 = db.Column(db.Time, primary_key=True)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    rest = db.Column(db.String(1))
    imei = db.Column(db.String(50))
    battery = db.Column(db.String(3))
    出発時間 = db.Column(db.Time)
    事業所CD = db.Column(db.String(4))
    status = db.Column(db.String(20))
    
    @staticmethod
    def find_data(date, time, savsid, jigyosyo, time1, time2):
        from app import db
        
        sql = ""
        sql += "select 日付,時間,lat,lng,id,rest,imei,battery,出発時間,事業所CD,status from " + 'posSavs'
        #検索条件
        where = ""
        where += " where 1=1"
        if date != '':
            where += " and 日付='" + str(date) + "'"
        
        if time != '':
            where += " and 時間='" + str(time) + "'"
        
        if savsid != '':
            where += " and id='" + str(savsid) + "'"
        
        if time1 != '':
            where += " and 時間>='" + str(time1) + "'"
        
        if time2 != '':
            where += " and 時間<='" + str(time2) + "'"
        
        if jigyosyo != '':
            where += " and 事業所CD='" + str(jigyosyo) + "'"
        
        #並び順
        order = ""
        order += " order by LPAD(id,4,0)"        
        return db.engine.execute(sql + where + order)
    
    @staticmethod
    def find_pos(_date, _time, lat, lng, dist):
        sql = ""
        sql += "select 事業所CD,日付, 時間, lat, lng, id, rest"
        #sql += ", (6378 * acos(cos(radians(" + lat + ")) * cos(radians(lat)) * cos(radians(lng) - radians(" + lng + ")) + sin(radians(" + lat + ")) * sin(radians(lat)))) AS distance"
        sql += " from posSavs"
        #sql += " HAVING distance < " + dist + "ORDER BY distance"
        
        return db.engine.execute(sql)
        



