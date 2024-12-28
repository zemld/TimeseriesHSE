from moex_request import MOEXRequestAttributes


class MOEXConnector:
    _action_request: str = 'https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/'
    _bond_request: str = 'https://iss.moex.com/iss/history/engines/bonds/markets/shares/boards/TQBR/securities/'

    
    def _create_request(self, request_body: str, attributes: MOEXRequestAttributes):
        pass

    
    def get_actions(self, attributes: MOEXRequestAttributes, result_format: str):
        pass


    def get_bonds(self, attributes: MOEXRequestAttributes, result_format: str):
        pass