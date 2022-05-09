from app import db


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
    def find_data_binninzu(id=None, date=None, binkbn=None, deptime=None):
        from app import db

        sql = ""
        sql += "select count(*) as CNT,sum(if(c.降車時刻 is not null,0,1)) as CZ"
        sql += " ,if(sum(if(((carStatus is null)and(userStatus is not null)),'1','0'))>0,'休み',null) as userStatus"
        sql += " from mergedata a"
        sql += " left join bindatad c on ((a.日付=c.日付)and(a.送迎区分=c.送迎区分)and(a.事業所CD=c.事業所CD)and(a.利用者番号=c.利用者番号))"
        sql += " where a.休=0"

        if date:
            sql += str(" AND a.日付='" + str(date)) + "'"

        if id:
            sql += str(" AND a.carId='" + str(id)) + "'"

        # if (isset($binkbn) && !empty($binkbn)) {
        # $sql .= " AND a.送迎区分='" . $binkbn . "'";
        # }

        if deptime:
            sql += str(" AND a.出発時間='" + str(deptime)) + "'"

        # $sql .= " and a.id<50";
        sql += " and ((a.利用者番号 is not null)or(Left(a.利用者番号,1)='A')or(Left(a.利用者番号,1)='E'))"

        return db.engine.execute(sql)


class PosSave(db.Model):
    __tablename__ = "posSavs"

    id = db.Column(db.String(3), primary_key=True)
    日付 = db.Column(db.Date)
    時間 = db.Column(db.Time)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    rest = db.Column(db.String(1))
    imei = db.Column(db.String(50))
    battery = db.Column(db.String(3))
    出発時間 = db.Column(db.Time)
    事業所CD = db.Column(db.String(4))
    status = db.Column(db.String(20))



