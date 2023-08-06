# import os,sys
# os.chdir(sys.path[0])
from query_toolkits.extractor import Extractor
from query_toolkits.error_correction import Corrector

et = Extractor()
extract_time = et.extract_time
extract_number = et.extract_number
extract_requirement = et.extract_requirement
extract_reference_no = et.extract_reference_no
extract_letters = et.extract_letters
extract_financial_index = et.extract_financial_index
extract_fund_name = et.extract_fund_name
extract_stock_name = et.extract_stock_name
extract_product_name = et.extract_product_name
extract_index_name = et.extract_index_name


c = Corrector()
correct = c.correct
