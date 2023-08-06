from PyQt5.QtCore import QVariant
from PyQt5.QAxContainer import QAxWidget

class pySBtraderOCX():

	def __init__(self, ocx):

		self.SBtrader = QAxWidget(ocx)

	def doConnect(self):
		"""
			Returns:
				`int`: 성공 1, 실패 0
		"""
		
		return self.SBtrader.dynamicCall("DoConnect()")
	
	def generateDocumentation(self):
		"""
			Returns:
				`str`: ocx documentation
		"""

		return self.SBtrader.generateDocumentation()
		
	def doLogin(self, nUserType, id, pwd, cert_pwd):
		"""
			Args:
				nUserType`int`: 0: 실시간, 2: 모의
				nMedDivCd`int`: 매체구분코드 현재는 고정값 (4: OPENAPI)
		"""

		self.SBtrader.dynamicCall("DoLogin(QInt, QString, QString, QString, QInt)", nUserType, id, pwd, cert_pwd, 4)

	def doMasterDownload(self):

		self.SBtrader.dynamicCall("DoMasterDownload()")

	def getEncodeText(self, pwd: str):
		"""
			Returns:
			`str`: 암호화 64자리 비밀번호
		"""
		
		return self.SBtrader.dynamicCall("GetEncodeText(QString)", pwd)
	
	def doRequestDomNewOrder(self, ipDayNight: str, ipAccNum: str, ipPassword: str, ipCode: str, ipBuySell: str, 
								ipOrderType: str, ipFillType: str, ipOrderQty: str, ipOrderPx: str, ipUserArea: str):
		"""
			Returns:
				`str`: -1 (오류), 양수(시퀀스값)
		"""

		self.SBtrader.dynamicCall("DoRequestDomNewOrder(QString, QString, QString, QString, QString, QString, QString, QString, QString, QString)", 
									[ipDayNight, ipAccNum, ipPassword, ipCode, ipBuySell, ipOrderType, ipFillType, ipOrderQty, ipOrderPx, ipUserArea])
		

	def doRequestGlbNewOrder(self, ipAccNum: str, ipPassword: str, ipCode: str, ipBuySell: str, 
									ipOrderType: str, ipOrderQty: str, ipOrderPx: str, ipStopPx: str, ipOrdDivType: str, ipOrdEdDate: str, ipUserArea: str):
		"""
			Returns:
				`str`: -1 (오류), 양수(시퀀스값)
		"""

		return self.SBtrader.dynamicCall("DoRequestGlbNewOrder(QString, QString, QString, QString, QString, QString, QString, QString, QString, QString, QString)", 
									[ipAccNum, ipPassword, ipCode, ipBuySell, ipOrderType, ipOrderQty, ipOrderPx, ipStopPx, ipOrdDivType, ipOrdEdDate, ipUserArea])
		
									
	def doRequestDomModifyOrder(self, ipDayNight: str, ipAccNum: str, ipPassword: str, ipCode: str, ipBuySell: str, 
								ipOrderType: str, ipFillType: str, ipOrderQty: str, ipOrderPx: str, ipOriOrdNum: str, ipUserArea: str):
		"""
			Returns:
				`str`: -1 (오류), 양수(시퀀스값)
		"""

		return self.SBtrader.dynamicCall("DoRequestDomModifyOrder(QString, QString, QString, QString, QString, QString, QString, QString, QString, QString, QString)", 
									[ipDayNight, ipAccNum, ipPassword, ipCode, ipBuySell, ipOrderType, ipFillType, ipOrderQty, ipOrderPx, ipOriOrdNum, ipUserArea])
	
	def doRequestGlbModifyOrder(self, ipAccNum: str, ipPassword: str, ipCode: str, ipBuySell: str, 
									ipOrderType: str, ipOrderQty: str, ipOrderPx: str, ipStopPx: str, ipOrdDivType: str, ipOrdEdDate: str, ipOriOrdNum, ipUserArea: str):
		"""
			Returns:
				`str`: -1 (오류), 양수(시퀀스값)
		"""

		return self.SBtrader.dynamicCall("DoRequestGlbModifyOrder(QString, QString, QString, QString, QString, QString, QString, QString, QString, QString, QString, QString)", 
									[ipAccNum, ipPassword, ipCode, ipBuySell, ipOrderType, ipOrderQty, ipOrderPx, ipStopPx, ipOrdDivType, ipOrdEdDate, ipOriOrdNum, ipUserArea])
		
	def doRequestDomCancelOrder(self, ipDayNight: str, ipAccNum: str, ipPassword: str, ipCode: str, ipBuySell: str, 
								ipOrderQty: str, ipOriOrdNum: str, ipUserArea: str):
		"""
			Returns:
				`str`: -1 (오류), 양수(시퀀스값)
		"""

		return self.SBtrader.dynamicCall("DoRequestDomCancelOrder(QString, QString, QString, QString, QString, QString, QString, QString)", 
									[ipDayNight, ipAccNum, ipPassword, ipCode, ipBuySell, ipOrderQty, ipOriOrdNum, ipUserArea])
		
	
	def doRequestGlbCancelOrder(self, ipAccNum: str, ipPassword: str, ipCode: str, ipBuySell: str, 
								ipOrderQty: str, ipOriOrdNum: str, ipUserArea: str):
		"""
			Returns:
				`str`: -1 (오류), 양수(시퀀스값)
		"""

		return self.SBtrader.dynamicCall("DoRequestGlbCancelOrder(QString, QString, QString, QString, QString, QString, QString)", 
									[ipAccNum, ipPassword, ipCode, ipBuySell, ipOrderQty, ipOriOrdNum, ipUserArea])
	
	def doRegistReal(self, ipTrCode: str, ipKeyCode: str):

		return self.SBtrader.dynamicCall("DoRegistReal(QString, QString)", ipTrCode, ipKeyCode)

	def doUnRegistReal(self, ipTrCode: str, ipKeyCode: str):

		return self.SBtrader.dynamicCall("DoUnRegistReal(QString, QString)", ipTrCode, ipKeyCode)
	
	def doRequestData(self, nMarket: int, ipTrCode: str, ipBuff: str, ipNextKey: str, ipUserArea: str):

		return self.SBtrader.dynamicCall("DoRequestData(QInt, QString, QString, QString, QString)", nMarket, ipTrCode, ipBuff, ipNextKey, ipUserArea)
	
	def doGetAccountInfCount(self):
		"""
			Returns:
				cnt`int`: 계좌 건수
		"""

		cnt = self.SBtrader.dynamicCall("DoGetAccountInfCount()")
		return cnt
	
	def doGetAccountInf(self, nIndex: int):
		"""
			Args:
				nIndex`int`: 계좌 인덱스
			
			Returns:
				pszAccountNo`str`: 계좌번호
		"""
		
		nIndex = QVariant(nIndex)
		pszAccountNo = QVariant('')
		pszAccountName = QVariant('')
		args = [nIndex, pszAccountNo, pszAccountName]
		
		self.SBtrader.dynamicCall("DoGetAccountInf(int, string&, string&)", args)

		return args[1]