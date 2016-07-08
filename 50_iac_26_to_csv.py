"""
50 IAC 26 To CSV file format conversion tool
By Chris Hartley
chris.hartley@renewindianapolis.org

Released under the GPL V3.

"""

import argparse
import csv

# used for progress bar
from tqdm import tqdm


"""
These file formats are defined in Chapter 50, Article 26 of the Indiana Administrative Code:
http://www.in.gov/dlgf/files/50_IAC_26_New_File_Formats.pdf. 

I extracted the tables (page 47-55) to CSV using Tabula (http://tabula.technology) then used a
LibreOffice formula to format as a dictionary. 

It should be fairly easy to add other 50 IAC 26 file formats using this same technique if you have the need.

"""

supported_formats = {
    'SALECONTAC': (
        {'field_name': 'SDF_ID', 'start': 1, 'end': 16},
        {'field_name': 'Contact_Instance_No', 'start': 17, 'end': 19},
        {'field_name': 'Contact_Type', 'start':20, 'end':20},
        {'field_name': 'FirstName',  'start':21, 'end':50},
        {'field_name': 'MiddleName', 'start':51, 'end':65},
        {'field_name': 'LastName', 'start':66, 'end':95},
        {'field_name': 'Suffix', 'start':96, 'end':105},
        {'field_name': 'Title', 'start':106, 'end':145},
        {'field_name': 'Company', 'start':146, 'end':205},
        {'field_name': 'Street1', 'start':206, 'end':265},
        {'field_name': 'Street2', 'start':266, 'end':325},
        {'field_name': 'City', 'start':326, 'end':355},
        {'field_name': 'State', 'start':356, 'end':357},
        {'field_name': 'PostalCode', 'start':358, 'end':367},
        {'field_name': 'Phone', 'start':368, 'end':387},
        {'field_name': 'Extension', 'start':388, 'end':397},
        {'field_name': 'EmailAddress', 'start':398, 'end':469},
        {'field_name': 'Sign_Verified', 'start':470, 'end':470},
        {'field_name': 'Email Tax Statement', 'start':471, 'end':471}

    ),

    'SALEPARCEL': (
        {'field_name': 'SDF_ID', 'start': 1, 'end': 16},
        {'field_name': 'Parcel_Instance_No', 'start': 17, 'end': 19},
        {'field_name': 'A1_Parcel_Number', 'start': 20, 'end': 37},
        {'field_name': 'A1_Subdiv_Name', 'start': 38, 'end': 87},
        {'field_name': 'A1_Subdiv_Lot_Num', 'start': 88, 'end': 92},
        {'field_name': 'A2_Split', 'start': 93, 'end': 93},
        {'field_name': 'A3_Land', 'start': 94, 'end': 94},
        {'field_name': 'A4_Improvement', 'start': 95, 'end': 95},
        {'field_name': 'A5_Street1', 'start': 96, 'end': 155},
        {'field_name': 'A5_City', 'start': 156, 'end': 185},
        {'field_name': 'A5_State', 'start': 186, 'end': 187},
        {'field_name': 'A5_PostalCode', 'start': 188, 'end': 197},
        {'field_name': 'A6_Street1', 'start': 198, 'end': 257},
        {'field_name': 'A6_City', 'start': 258, 'end': 287},
        {'field_name': 'A6_State', 'start': 288, 'end': 289},
        {'field_name': 'A6_PostalCode', 'start': 290, 'end': 299},
        {'field_name': 'A7_Legal_Description', 'start': 300, 'end': 799},
        {'field_name': 'P2_1_Parcel_Num_Verified', 'start': 800, 'end': 817},
        {'field_name': 'P2_2_AV_Land', 'start': 818, 'end': 829},
        {'field_name': 'P2_3_AV_Improvement', 'start': 830, 'end': 841},
        {'field_name': 'P2_4_AV_PersProp', 'start': 842, 'end': 853},
        {'field_name': 'P2_5_Total_AV', 'start': 854, 'end': 865},
        {'field_name': 'P2_6_Prop_Class_Code', 'start': 866, 'end': 868},
        {'field_name': 'P2_7_Neighborhood_Code', 'start': 869, 'end': 878},
        {'field_name': 'P2_8_Tax_District', 'start': 879, 'end': 881},
        {'field_name': 'P2_9_Acreage', 'start': 882, 'end': 893},
        {'field_name': 'F3_Homestead_Verified', 'start': 894, 'end': 894},
        {'field_name': 'F4_Solar_Verified', 'start': 895, 'end': 895},
        {'field_name': 'F5_Wind_Verified', 'start': 896, 'end': 896},
        {'field_name': 'F6_Hydroelectric_Verified', 'start': 897, 'end': 897},
        {'field_name': 'F7_Geothermal_Verified', 'start': 898, 'end': 898},
        {'field_name': 'F8_Res_Rental_Verified', 'start': 899, 'end': 899},
    ),


    'SALEDISC': (
        {'field_name': 'SDF_ID', 'start': 1, 'end': 16},
        {'field_name': 'County_ID', 'start': 17, 'end': 18},
        {'field_name': 'County_Name', 'start': 19, 'end': 43},
        {'field_name': 'B1_Valuable_Consider', 'start': 44, 'end': 44},
        {'field_name': 'B2_Buyer_Adjacent', 'start': 45, 'end': 45},
        {'field_name': 'B3_Vacant_Land', 'start': 46, 'end': 46},
        {'field_name': 'B4_Trade', 'start': 47, 'end': 47},
        {'field_name': 'B4_Trade_Assessor ', 'start': 48, 'end': 48},
        {'field_name': 'B5_Seller_Points ', 'start': 49, 'end': 49},
        {'field_name': 'B6_Primary_Change ', 'start': 50, 'end': 50},
        {'field_name': 'B7_Relationship ', 'start': 51, 'end': 51},
        {'field_name': 'B8_Land_Contract ', 'start': 52, 'end': 52},
        {'field_name': 'B8_Land_Contract_Term ', 'start': 53, 'end': 56},
        {'field_name': 'B8_Land_Contract_Date ', 'start': 57, 'end': 66},
        {'field_name': 'B9_PersProp ', 'start': 67, 'end': 67},
        {'field_name': 'B10_Physical_Change ', 'start': 68, 'end': 68},
        {'field_name': 'B11_Partial_Interest ', 'start': 69, 'end': 69},
        {'field_name': 'B12_Court_Order ', 'start': 70, 'end': 70},
        {'field_name': 'B13_Partition ', 'start': 71, 'end': 71},
        {'field_name': 'B14_Charity ', 'start': 72, 'end': 72},
        {'field_name': 'B15_Easement ', 'start': 73, 'end': 73},
        {'field_name': 'C1_Conveyance_Date', 'start': 74, 'end': 83},
        {'field_name': 'C2_Num_Parcels', 'start': 84, 'end': 87},
        {'field_name': 'C3_Special_Comment', 'start': 88, 'end': 342},
        {'field_name': 'C4_Relationship', 'start': 343, 'end': 343},
        {'field_name': 'C4_Discount', 'start': 344, 'end': 357},
        {'field_name': 'C5_Value_PersProp', 'start': 358, 'end': 371},
        {'field_name': 'C6_Sales_Price', 'start': 372, 'end': 385},
        {'field_name': 'C7_Seller_Financed', 'start': 386, 'end': 386},
        {'field_name': 'C8_Buyer_Loan', 'start': 387, 'end': 387},
        {'field_name': 'C9_Mortgage_Loan', 'start': 388, 'end': 388},
        {'field_name': 'C10_Amount_Loan', 'start': 389, 'end': 402},
        {'field_name': 'C11_Interest_Rate', 'start': 403, 'end': 408},
        {'field_name': 'C12_Points', 'start': 409, 'end': 422},
        {'field_name': 'C13_Amortization_Period', 'start': 423, 'end': 425},
        {'field_name': 'F1_Primary_Residence', 'start': 426, 'end': 426},
        {'field_name': 'F1_CountyNumber', 'start': 427, 'end': 428},
        {'field_name': 'F1_Street1', 'start': 429, 'end': 488},
        {'field_name': 'F1_City', 'start': 489, 'end': 518},
        {'field_name': 'F1_State', 'start': 519, 'end': 520},
        {'field_name': 'F1_PostalCode', 'start': 521, 'end': 530},
        {'field_name': 'F1_County', 'start': 531, 'end': 555},
        {'field_name': 'F2_Vacated_Homestead', 'start': 556, 'end': 556},
        {'field_name': 'F2_CountyNumber', 'start': 557, 'end': 558},
        {'field_name': 'F2_Street1', 'start': 559, 'end': 618},
        {'field_name': 'F2_City', 'start': 619, 'end': 648},
        {'field_name': 'F2_State', 'start': 649, 'end': 650},
        {'field_name': 'F2_PostalCode', 'start': 651, 'end': 660},
        {'field_name': 'F2_County', 'start': 661, 'end': 685},
        {'field_name': 'F3_Homestead', 'start': 686, 'end': 686},
        {'field_name': 'F4_Solar', 'start': 687, 'end': 687},
        {'field_name': 'F5_Wind', 'start': 688, 'end': 688},
        {'field_name': 'F6_Hydroelectric', 'start': 689, 'end': 689},
        {'field_name': 'F7_Geothermal', 'start': 690, 'end': 690},
        {'field_name': 'F8_Res_Rental', 'start': 691, 'end': 691},
        {'field_name': 'P2_10_Physical_Changes', 'start': 692, 'end': 1191},
        {'field_name': 'P2_11_Form_Complete', 'start': 1192, 'end': 1192},
        {'field_name': 'P2_12_Fee_Required', 'start': 1193, 'end': 1193},
        {'field_name': 'P2_13_Date_Sale', 'start': 1194, 'end': 1203},
        {'field_name': 'P2_14_Date_Received', 'start': 1204, 'end': 1213},
        {'field_name': 'P2_15_Special_Circum', 'start': 1214, 'end': 1713},
        {'field_name': 'P2_16_Valid_Trending', 'start': 1714, 'end': 1714},
        {'field_name': 'P2_17_Validation_Complete', 'start': 1715, 'end': 1715},
        {'field_name': 'P2_18_Validated_By', 'start': 1716, 'end': 1740},
        {'field_name': 'P2_Assessor_Stamp', 'start': 1741, 'end': 1741},
        {'field_name': 'P3_1_Disclosure_Fee', 'start': 1742, 'end': 1745},
        {'field_name': 'P3_2_Local_Fee', 'start': 1746, 'end': 1749},
        {'field_name': 'P3_3_Total_Fee', 'start': 1750, 'end': 1753},
        {'field_name': 'P3_4_Receipt_Num', 'start': 1754, 'end': 1778},
        {'field_name': 'P3_5_Transfer_Date', 'start': 1779, 'end': 1788},
        {'field_name': 'P3_6_Form_Complete', 'start': 1789, 'end': 1789},
        {'field_name': 'P3_7_Fee_Collected', 'start': 1790, 'end': 1790},
        {'field_name': 'P3_8_Attach_Complete', 'start': 1791, 'end': 1791},
        {'field_name': 'P3_Auditor_Stamp', 'start': 1792, 'end': 1792},
    ),
}

def extract_data(input_file, output_file, file_format):
    record = {}
    fieldnames = []
    pp = pprint.PrettyPrinter(indent=4)
    with open(input_file, 'r') as source_file:
        with open(output_file, 'wb') as csvfile:
            for field in file_format: # create list of columns/fieldnames in given file format
                fieldnames.append(field['field_name'])

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')
            writer.writeheader()

            for line in tqdm(source_file):
                if line[0:6] == 'TRAILER': # last line, includes some verification stuff probably but we like to live dangerously
                    pass
                if line[0:3] == 'SALE': # first header line, includes source information, etc but ignore all that
                    pass
                else:
                    for field in file_format:
                       record[field['field_name']] = line[int(field['start'])-1:int(field['end'])-1].strip() # we convert from 1 index as used in 50 IAC 26 to 0 index, as used by python
                    writer.writerow(record)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert various files formatted per 50 IAC 26 to CSV format')
    parser.add_argument('-i', '--input', help='50 IAC 26 formated input file', required=True)
    parser.add_argument('-o', '--output', help='CSV formated output file, default input file + .csv', required=True)
    parser.add_argument('-t', '--type', help='Format of file', choices=['SALEDISC', 'SALECONTAC','SALEPARCEL'], required=True)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')

    args = parser.parse_args()
    i = args.input
    o = args.output
    t = supported_formats[args.type] 
    extract_data(i,o,t)

