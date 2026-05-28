import argparse


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="HDF5 input file")
    parser.add_argument("outputfile", help="BUFR output file")

    args = parser.parse_args()

    # FAI_COSE


if __name__ == '__main__':
    # Questo serve per eseguirla con python -m simcradarlib.cli.vadprofiles_hdf2bufr, ma una volta installata la
    # libreria puoi lanciarla con simcradarlib-vadprofiles_hdf2bufr (possiamo cambiare il nome se vuoi).
    run_cli()
