from app import ma


class CarsSchema(ma.Schema):
    class Meta:
        fields = ('cnt', 'cars')


class NowposSchema(ma.Schema):
    class Meta:
        fields = ('id', '日付', '時間', '運転手', 'Posx', 'Posy', 'rest', 'battery', '出発時間', '事業所CD', 'status')


class DNowposSchema(ma.Schema):
    class Meta:
        fields = ('事業所CD', '事業所番号', '事業所名', 'lat', 'lng',)


class PosSaveSchema(ma.Schema):
    class Meta:
        fields = ('事業所CD', 'id', '日付', '時間', 'lng', 'lat', '出発時間', 'battery', 'imei',  'rest', 'status')


class PosSaveShortSchema(ma.Schema):
    class Meta:
        fields = ('id', '日付', '時間', 'lat', 'lng', 'rest', '事業所CD')
