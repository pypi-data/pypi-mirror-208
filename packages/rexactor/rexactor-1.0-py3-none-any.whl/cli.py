import tapcap
import os
import rexactor

def main():
    print("RExACtor: A Regular Expression Apriori Constructor")
    preThres = float(input("Prefix frequency threshold (0.0 - 1.0)? "))
    sufThres = float(input("Suffix frequency threshold (0.0 - 1.0)? "))
    filepath = input("File input path (PCAP, PCAPNG, or CSV)? ")
    while not os.path.isfile(filepath):
        print("File not found.")
        filepath = input("File input path (PCAP, PCAPNG, or CSV)? ")

    CSVextension = filepath[len(filepath) - 3:].lower()
    PCAPextension = filepath[len(filepath) - 4:].lower()
    PCAPNGextension = filepath[len(filepath) - 6:].lower()

    if PCAPextension == "pcap" or PCAPNGextension == "pcapng":
        tapcap.pcap2csv(filepath, "local.csv")
        filepath = "local.csv"
    elif CSVextension != "csv":
        print("Invalid source file provided. Must be .csv, .pcap, or .pcapng.")
        sys.exit()

    rexactor.main(filepath, preThres, sufThres)
