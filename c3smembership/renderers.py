import StringIO
import unicodecsv
from gnupg_encrypt import encrypt_with_gnupg


class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        fout = StringIO.StringIO()
        writer = unicodecsv.writer(
            fout, delimiter=';', quoting=unicodecsv.QUOTE_ALL)

        writer.writerow(value['header'])
        writer.writerows(value['rows'])

        resp = system['request'].response
        resp.content_type = 'text/csv'
        resp.content_disposition = 'attachment;filename="yes.csv"'
        return fout.getvalue()
#        return encrypt_with_gnupg(fout.getvalue())
