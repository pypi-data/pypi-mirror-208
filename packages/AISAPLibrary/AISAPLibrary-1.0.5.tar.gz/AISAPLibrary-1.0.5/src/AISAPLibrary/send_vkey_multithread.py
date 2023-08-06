from AISAPLibrary import AISAPLibrary
import sys

if __name__ == '__main__':
    try :
        sap = AISAPLibrary()
        sap.connect_to_session()
        sap.connect_to_existing_connection(sys.argv[1])
        sap.send_vkey_other_session(int(sys.argv[2]), int(sys.argv[3]), str(sys.argv[4]))
    except :
        print(sys.argv[1])
        print(sys.argv[2])
        print(sys.argv[3])
        print(sys.argv[4])
        print('Error in calling function please follow this order')