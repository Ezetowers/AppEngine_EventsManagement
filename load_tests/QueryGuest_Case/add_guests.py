from lxml import etree
import sys

REQUEST_BODY_PART_1 = '<![CDATA[actualEvent='
REQUEST_BODY_PART_2 = '&guestName=Phil&guestSurname=Collins&guestCompany=GenesisSRL&guestEmail='
REQUEST_BODY_PART_3 = '&checkDuplicates=false]]>'
CONTENT_TYPE = 'Content-type: application/x-www-form-urlencoded'


def usage():
    print "python create_test_case [URL]"\
        " [EVENT_NAME] [AMOUNT_CASES] [TEST_CASE_FILENAME]"


def main():
    if len(sys.argv) != 5:
        usage()

    root = etree.Element('testcases')
    url = sys.argv[1]
    event = sys.argv[2]
    amount_cases = int(sys.argv[3])
    test_case_filename = sys.argv[4]

    for case in range(1,amount_cases):
        case_node = etree.Element('case')
        etree.SubElement(case_node, 'url').text = url + "/add_guest"
        etree.SubElement(case_node, 'method').text = 'POST'
        body = REQUEST_BODY_PART_1 + event + REQUEST_BODY_PART_2 + "Email" + str(case) + REQUEST_BODY_PART_3
        etree.SubElement(case_node, 'body').text = body
        etree.SubElement(case_node, 'add_header').text = CONTENT_TYPE
        root.append(case_node)

    etree.ElementTree(root).write(test_case_filename,
                                  pretty_print=True,
                                  encoding='iso-8859-1')

# Line to indicate that this is the main
if __name__ == "__main__":
    main()
