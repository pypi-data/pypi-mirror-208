from datetime import datetime, timedelta

import boto3
import typeguard

from cloud_governance.common.clouds.aws.cost_explorer.cost_explorer_operations import CostExplorerOperations
from cloud_governance.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from cloud_governance.common.ldap.ldap_search import LdapSearch
from cloud_governance.common.logger.logger_time_stamp import logger_time_stamp
from cloud_governance.common.mails.mail_message import MailMessage
from cloud_governance.common.mails.postfix import Postfix
from cloud_governance.main.environment_variables import environment_variables


class CostOverUsage:
    """
    This class will monitor the cost explorer reports and send alert to the user if they exceed specified amount
    """

    DEFAULT_ROUND_DIGITS = 3
    FORECAST_GRANULARITY = 'MONTHLY'
    FORECAST_COST_METRIC = 'UNBLENDED_COST'
    OVER_USAGE_THRESHOLD = 0.05

    def __init__(self):
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__aws_account = self.__environment_variables_dict.get('account', '').replace('OPENSHIFT-', '').strip()
        self.__postfix_mail = Postfix()
        self.__mail_message = MailMessage()
        self.__es_host = self.__environment_variables_dict.get('es_host', '')
        self.__es_port = self.__environment_variables_dict.get('es_port', '')
        self.__over_usage_amount = self.__environment_variables_dict.get('CRO_COST_OVER_USAGE', '')
        self.__es_ce_reports_index = self.__environment_variables_dict.get('USER_COST_INDEX', '')
        self.__ldap_search = LdapSearch(ldap_host_name=self.__environment_variables_dict.get('LDAP_HOST_NAME', ''))
        self.__cro_admins = self.__environment_variables_dict.get('CRO_DEFAULT_ADMINS', [])
        self.es_index_cro = self.__environment_variables_dict.get('CRO_ES_INDEX', '')
        self.__cro_duration_days = self.__environment_variables_dict.get('CRO_DURATION_DAYS')
        self.current_end_date = datetime.utcnow()
        self.current_start_date = self.current_end_date - timedelta(days=self.__cro_duration_days)
        self.__public_cloud_name = self.__environment_variables_dict.get('PUBLIC_CLOUD_NAME')
        self.__ce_operations = CostExplorerOperations()
        self.es_operations = ElasticSearchOperations(es_host=self.__es_host, es_port=self.__es_port)
        self.__over_usage_threshold = self.OVER_USAGE_THRESHOLD * self.__over_usage_amount

    @typeguard.typechecked
    @logger_time_stamp
    def get_cost_based_on_tag(self, start_date: str, end_date: str, tag_name: str, extra_filters: any = None, extra_operation: str = 'And', granularity: str = None, forecast: bool = False):
        """
        This method gives the cost based on the tag_name
        :param forecast:
        :param granularity:
        :param extra_operation: default, And
        :param extra_filters:
        :param tag_name:
        :param start_date:
        :param end_date:
        :return:
        """
        remove_savings_cost = {  # removed the savings plan usage from the user costs
            'Not': {
                'Dimensions': {
                    'Key': 'RECORD_TYPE',
                    'Values': ['SavingsPlanRecurringFee', 'SavingsPlanNegation', 'SavingsPlanCoveredUsage']
                }
            }
        }
        Filters = remove_savings_cost
        if extra_filters:
            if type(extra_filters) == list:
                Filters = {
                    extra_operation: [
                        *extra_filters,
                        remove_savings_cost
                    ]
                }
            else:
                Filters = {
                    extra_operation: [
                        extra_filters,
                        remove_savings_cost
                    ]
                }
        if forecast:
            results_by_time = self.__ce_operations.get_cost_forecast(start_date=start_date, end_date=end_date, granularity=self.FORECAST_GRANULARITY, cost_metric=self.FORECAST_COST_METRIC, Filter=Filters)['Total']
            response = [{'Forecast': round(float(results_by_time.get('Amount')), self.DEFAULT_ROUND_DIGITS)}]
        else:
            results_by_time = self.__ce_operations.get_cost_by_tags(start_date=start_date, end_date=end_date, tag=tag_name, Filter=Filters, granularity=granularity)['ResultsByTime']
            response = self.__ce_operations.get_filter_data(ce_data=results_by_time, tag_name=tag_name)
        return response

    @typeguard.typechecked
    @logger_time_stamp
    def __get_start_end_dates(self, start_date: datetime = None, end_date: datetime = None):
        """
        This method return the start_date and end_date
        :param start_date:
        :param end_date:
        :return:
        """
        if not start_date and not end_date:
            end_date = self.current_end_date.date()
            start_date = self.current_start_date.replace(day=1).date()
        elif not start_date:
            start_date = self.current_start_date.date()
            end_date = end_date.date()
        else:
            if not end_date:
                end_date = self.current_end_date.date()
                start_date = start_date.date()
            start_date = start_date.date()
            end_date = end_date.date()
        return start_date, end_date

    @typeguard.typechecked
    @logger_time_stamp
    def get_monthly_user_es_cost_data(self, tag_name: str = 'User', start_date: datetime = None, end_date: datetime = None, extra_matches: any = None, granularity: str = 'MONTHLY', extra_operation: str = 'And'):
        """
        This method get the user cost from the es-data
        :param tag_name: by default User
        :param start_date:
        :param end_date:
        :param extra_matches:
        :param granularity: by default MONTHLY
        :param extra_operation:
        :return:
        """
        start_date, end_date = self.__get_start_end_dates(start_date=start_date, end_date=end_date)
        return self.get_cost_based_on_tag(start_date=str(start_date), end_date=str(end_date), tag_name=tag_name, granularity=granularity, extra_filters=extra_matches, extra_operation=extra_operation)

    def get_forecast_cost_data(self, tag_name: str = 'User', start_date: datetime = None, end_date: datetime = None, extra_matches: any = None, granularity: str = 'MONTHLY', extra_operation: str = 'And'):
        """
        This method return the forecast based on inputs
        :param tag_name: by default User
        :param start_date:
        :param end_date:
        :param extra_matches:
        :param granularity: by default MONTHLY
        :param extra_operation:
        :return:
        """
        start_date, end_date = self.__get_start_end_dates(start_date=start_date, end_date=end_date)
        return self.get_cost_based_on_tag(start_date=str(start_date), end_date=str(end_date), tag_name=tag_name, granularity=granularity, extra_filters=extra_matches, extra_operation=extra_operation, forecast=True)

    @logger_time_stamp
    def get_cost_over_usage_users(self):
        """
        This method returns the cost over usage users which are not opened ticket
        :return:
        """
        over_usage_users = []
        current_month_users = self.get_monthly_user_es_cost_data()
        for user in current_month_users:
            user_name = user.get('User')
            cost = round(user.get('Cost'), self.DEFAULT_ROUND_DIGITS)
            if cost >= (self.__over_usage_amount - self.__over_usage_threshold):
                query = {  # check user opened the ticket in elastic_search
                    "query": {
                        "bool": {
                            "must": {
                                "term": {"user": user_name}
                            },
                            "filter": {
                                "range": {
                                    "timestamp": {
                                        "format": "yyyy-MM-dd",
                                        "lte": str(self.current_end_date.date()),
                                        "gte": str(self.current_start_date.date()),
                                    }
                                }
                            }
                        }
                    }
                }
                response = self.es_operations.fetch_data_by_es_query(es_index=self.es_index_cro, query=query)
                if not response:
                    over_usage_users.append(user)
                for cro_data in response:
                    project = cro_data.get('_source').get('project')
                    ticket_id_state = cro_data.get('_source').get('ticket_id_state')
                    if 'close' in ticket_id_state.lower():
                        ticket_closed_time = datetime.strptime(cro_data.get('_source').get('timestamp'), "%Y-%m-%dT%H:%M:%S.%f")
                        month_start_date = ticket_closed_time if self.current_start_date < ticket_closed_time else self.current_start_date
                        user_response = self.get_monthly_user_es_cost_data(start_date=month_start_date, extra_matches={'Tags': {'Key': 'User', 'Values': [user_name]}}, extra_operation='And', tag_name='Project')
                        if user_response:
                            if project in [res.get('Project') for res in user_response]:
                                user_cost = round(user_response[0].get('Cost'), self.DEFAULT_ROUND_DIGITS)
                                user['Cost'] = user_cost
                                user['Project'] = project
                                if user_cost >= self.__over_usage_amount:
                                    over_usage_users.append(user)
        return over_usage_users

    @logger_time_stamp
    def send_alerts_to_over_usage_users(self):
        """
        This method send alerts to cost over usage users
        :return:
        """
        users_list = self.get_cost_over_usage_users()
        for row in users_list:
            user, cost, project = row.get('User'), row.get('Cost'), row.get('Project', '')
            cc = [*self.__cro_admins]
            user_details = self.__ldap_search.get_user_details(user_name=user)
            if user_details:
                name = f'{user_details.get("FullName")}'
                cc.append(user_details.get('managerId'))
                subject, body = self.__mail_message.cro_cost_over_usage(CloudName=self.__public_cloud_name,
                                                                        OverUsageCost=self.__over_usage_amount,
                                                                        FullName=name, Cost=cost, Project=project, to=user)
                self.__postfix_mail.send_email_postfix(to=user, cc=cc, content=body, subject=subject, mime_type='html')
        return [row.get('User') for row in users_list]

    @logger_time_stamp
    def run(self):
        """
        This method run the cost over usage methods
        :return:
        """
        return self.send_alerts_to_over_usage_users()
