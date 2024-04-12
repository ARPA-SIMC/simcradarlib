import logging
from datetime import datetime
from typing import Optional

module_logger = logging.getLogger(__name__)


def log_endprocess_info(start_time: datetime) -> None:

    """
    Funzione che stampa l'avviso della fine delle operazioni di uno script e il tempo totale di esecuzione
    dall'istante passato in input nell'oggetto datetime start_time.

    INPUT  :  logger      --logging.Logger  : logger definito nel main
              start_time  --datetime        : oggetto datetime.datetime dell'istante iniziale delle operazioni

    OUTPUT :  None
    """
    end_time = datetime.now()
    diff = end_time - start_time
    try:
        diff_sec = diff.total_seconds()
    except AttributeError:

        def total_seconds(td):
            return float((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)) / 10**6

        diff_sec = total_seconds(diff)
    module_logger.debug(f"Durata processo: {diff_sec} secondi")
    module_logger.debug(f"################ FINE OPERAZIONI - {end_time} ########################")


def log_subprocess_info(t_start_processo: datetime) -> None:

    """
    Funzione che stampa il tempo di esecuzione per un sottoprocesso
    tra l'istante passato in input t_start_processo, che deve corrispondere
    all'inizio del sottoprocesso, e l'istante di chiamata di questo metodo.

    INPUT:
    -t_start_processo  --datetime : oggetto datetime.datetime dell'istante
                                    in cui ha avuto inizio il sottoprocesso
                                    di cui voglio conoscere il tempo di esecuzione
    OUTPUT:None
    """

    partial_time = datetime.now()
    diff = partial_time - t_start_processo
    try:
        diff_sec = diff.total_seconds()
    except AttributeError:

        def total_seconds(td):
            return float((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)) / 10**6

        diff_sec = total_seconds(diff)
    module_logger.info(f"Durata processo: {diff_sec} secondi")
