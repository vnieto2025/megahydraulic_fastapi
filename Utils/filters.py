from Models.report_model import ReportModel
from Utils.tools import CustomException
from datetime import datetime, timedelta

class Filters:
    
    def get_filters(self, data: dict):

        try:
            filter_query = []
            filter_query.extend(self.om_filter(data))
            filter_query.extend(self.solped_filter(data))
            filter_query.extend(self.buy_order_filter(data))
            filter_query.extend(self.client_filter(data))
            filter_query.extend(self.dates_filter(data))

            return filter_query

        except Exception as ex:
            raise CustomException(str(ex))

    # return the list by om param
    def om_filter(self, data: dict):

        filter = []
        om = data.get("om") != None and data.get("om") != ""
        if om:
            filter.append(ReportModel.om.like(f'%{data["om"]}%'))

        return filter

    # return the list by solped param
    def solped_filter(self, data: dict):

        filter = []
        solped = data.get("solped") != None and data.get("solped") != ""
        if solped:
            filter.append(ReportModel.solped.like(f'%{data["solped"]}%'))

        return filter

    # return the list by solped param
    def buy_order_filter(self, data: dict):

        filter = []
        buy_order = data.get("buy_order") != None and data.get("buy_order") != ""
        if buy_order:
            filter.append(ReportModel.buy_order.like(f'%{data["buy_order"]}%'))

        return filter

    # return the list by client id param
    def client_filter(self, data: dict):

        filter = []
        client_id = data.get("client_id") != None and data.get("client_id") != ""
        if client_id:
            filter.append(ReportModel.client_id.like(f'%{data["client_id"]}%'))

        return filter

    # return the list by dates param
    def dates_filter(self, data: dict):

        filter = []
        
        filter_start_date = data.get("start_date") != None and data.get("start_date") != ""
        filter_end_date = data.get("end_date") != None and data.get("end_date") != ""

        if filter_start_date and filter_end_date:
            date_format = '%Y-%m-%d'

            complete_start_date = str(data.get("start_date")) + " 00:00:00"
            complete_end_date = str(data.get("end_date")) + " 23:59:59"

            start_date = datetime.strptime(data["start_date"], date_format).date()
            end_date = datetime.strptime(data["end_date"], date_format).date()


            if start_date > end_date:
                msg = "La fecha inicial no puede ser mayor a la fecha final."
                raise CustomException(msg)
            filter.append(ReportModel.created_at.between(
                complete_start_date, complete_end_date))

        return filter
