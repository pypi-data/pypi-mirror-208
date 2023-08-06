import json
import logging
import requests
from sqlalchemy import create_engine
import pandas as pd


class PortfolioInfo:
    def __init__(self, paper_trading_db_host: str, paper_trading_db_port: int, paper_trading_db_username: str,
                 paper_trading_db_password: str, paper_trading_db_name: str, paper_trading_api_end_point: str, ai_portfolio_service_host: str):
        self.paper_trading_db_host = paper_trading_db_host
        self.paper_trading_db_port = paper_trading_db_port
        self.paper_trading_db_username = paper_trading_db_username
        self.paper_trading_db_password = paper_trading_db_password
        self.paper_trading_db_name = paper_trading_db_name
        self.paper_trading_api_end_point = paper_trading_api_end_point
        self.ai_portfolio_service_host = ai_portfolio_service_host

        paper_trading_db_connection_str = f'postgresql://{paper_trading_db_username}:{paper_trading_db_password}@{paper_trading_db_host}:{paper_trading_db_port}/{paper_trading_db_name}'
        self.paper_trading_db_connection = create_engine(
            paper_trading_db_connection_str).connect()

    def get_all_portfolio(self):
        return pd.read_sql(f""" 
            select t1."portfolioConfigId",t4."tradingModel",t4."portfolioModel",t1.username,t1.symbol,COALESCE("latestMatchPrice",0) as "latestMatchPrice",
                "totalAmount",CASE WHEN "forceSellAmount" > "availableAmount" THEN 0 ELSE "availableAmount" - "forceSellAmount"  END as "availableAmount",
                "scheduledAmount", "averageMatchedPrice","targetPercent",
                "balance","initBalance", t1."cutoffDate", "forceSellAmount" , t1."portfolioType"
                from "portfolio" t1
                left join "symbol_info" t2 on t1.symbol = t2.symbol
                left join "portfolio_config" t4 on t1."portfolioConfigId" = t4.id
				WHERE t4.status = 'RUNNING'
        """, con=self.paper_trading_db_connection)

    def update_target_percent_portfolio(self, portfolio_data: dict, cycle_length: int, portfolioModel: int):

        url = f"{self.paper_trading_api_end_point}/portfolioRatio/updateNewRatio"

        payload = json.dumps({
            "ratio": portfolio_data,
            "portfolioModel": portfolioModel
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if(response.status_code == 200):
            logging.info(
                f'update_target_percent_portfolio ==> {response.text}')
        else:
            logging.error(
                f'update_target_percent_portfolio ==> {response.text}')
            raise Exception('update_target_percent_portfolio failed')

        ### hard code backtest môi trường dev ###
        try:
            url = f"http://10.11.0.99:31377/portfolioRatio/updateNewRatio"

            payload = json.dumps({
                "ratio": portfolio_data,
                "portfolioModel": portfolioModel
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request(
                "POST", url, headers=headers, data=payload)

            if(response.status_code == 200):
                logging.info(
                    f'update_target_percent_portfolio ==> {response.text}')
            else:
                logging.error(
                    f'update_target_percent_portfolio ==> {response.text}')
                raise Exception('update_target_percent_portfolio failed')
        except:
            logging.error('fail update dev environment')
            pass
