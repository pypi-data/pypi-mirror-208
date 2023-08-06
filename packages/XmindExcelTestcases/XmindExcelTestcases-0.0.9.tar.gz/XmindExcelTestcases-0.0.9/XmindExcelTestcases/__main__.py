import sys
from XmindExcelTestcases.convert_xmind_to_excel import ConvertXmindToExcel

def main():
    para_list = sys.argv[1:]
    if len(para_list) == 3:
        ConvertXmindToExcel().convert(para_list[0], para_list[1], ignore_layer_number=para_list[2])
    else:
        ConvertXmindToExcel().convert(para_list[0], para_list[1])
    sys.exit()

if __name__ == '__main__':
    main()