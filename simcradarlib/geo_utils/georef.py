import osgeo.osr as osr
import numpy as np
import logging

"""
Il modulo simcradarlib.geo_utils.georef contiene utilities per la georeferenziazione
di dati radar volumetrici. In particolare, le routines sono quelle implementate in wradlib:

                https://docs.wradlib.org/en/latest/index.html
"""

module_logger = logging.getLogger(__name__)


def bin_altitude(r, theta, sitealt, *, re=6371000, ke=4.0 / 3.0):

    """
    Calcola l'altezza del bin radar tenendo conto della rifrattività atmosferica,
    usando la formula in `Doviak1993`:

    .. math::

        h = \\sqrt{r^2 + (k_e r_e)^2 + 2 r k_e r_e \\sin\\theta} - k_e r_e

    INPUT:
    - r        --np.ndarray               : array dei ranges [m]
    - theta    --Union[np.ndarray, float] : array degli angoli di elevazione in gradi,
                                            con 0° all'orizzonte e +90° la direzione di
                                            puntamento sulla verticale del radar.
    - sitealt  --float                    : altezza in [m] s.l.m. del sito radar
    - re       --float = 6371000          : raggio terrestre [m] (default 6371000 m).
    - ke       --Optional[float]=4/3      : fattore di aggiustamento per tener conto
                                            della dipendenza della propagazione del
                                            segnale radar dal gradiente di rifrattività.
                                            Il valore di default 4/3 è una buona approssimazione
                                            per quasi tutte le lunghezze d'onda.
    OUTPUT:
    --np.ndarray : array delle altezze dei bin radar in [m]
    """

    reff = ke * re
    sr = reff + sitealt
    return np.sqrt(r**2 + sr**2 + 2 * r * sr * np.sin(np.radians(theta))) - reff


def site_distance(r, theta, binalt, *, re=6371000, ke=4.0 / 3.0):

    """
    Calcola la distanza ortodromica dal bin a una certa altezza e il sito radar,
    su una terra sferica e tenendo conto della rifrattività atmosferica.

    La formula per la distanza, da `Doviak1993`, è:
    .. math::

        s = k_e r_e \\arcsin\\left(
        \\frac{r \\cos\\theta}{k_e r_e + h_n(r, \\theta, r_e, k_e)}\\right)

    dove :math:`h_n` è l'output di simcradarlib.geo_utils.georef.bin_altitude.

    INPUT:
    -r        --np.ndarray               : array dei ranges [m]
    -theta    --Union[np.ndarray, float] : array degli angoli di elevazione in gradi,
                                           con 0° all'orizzonte e +90° la direzione di
                                           puntamento sulla verticale del radar.
    -binalt  --np.ndarray                : array dell'altezza [m] del sito radar, con
                                           stessa shape di r.
    -re      --float = 6371000           : raggio terrestre [m] (default 6371000 m).
    -ke      --Optional[float]=4/3       : fattore di aggiustamento per tener conto
                                           della dipendenza della propagazione del
                                           segnale radar dal gradiente di rifrattività.
                                           Il valore di default 4/3 è una buona approssimazione
                                           per quasi tutte le lunghezze d'onda.
    OUTPUT:
    --np.ndarray    : array delle distanze ortodromiche [m].
    """

    reff = ke * re
    return reff * np.arcsin(r * np.cos(np.radians(theta)) / (reff + binalt))


def get_earth_radius(latitude, *, sr=None):

    """
    Restituisce il raggio terrestre [km] per un dato modello di sferoide (sr) ad
    una data posizione.

    .. math::

        R^2 = \\frac{a^4 \\cos(f)^2 + b^4 \\sin(f)^2}
        {a^2 \\cos(f)^2 + b^2 \\sin(f)^2}

    INPUT:
    -sr       --class:`gdal:osgeo.osr.SpatialReference`  : spatial reference
    -latitude --float                                    : latitudine geodetica in gradi

    OUTPUT:
    radius    --float : raggio terrestre [m]
    """

    if sr is None:
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326)
    radius_e = sr.GetSemiMajor()
    radius_p = sr.GetSemiMinor()
    latitude = np.radians(latitude)
    radius = np.sqrt(
        (np.power(radius_e, 4) * np.power(np.cos(latitude), 2) + np.power(radius_p, 4) * np.power(np.sin(latitude), 2))
        / (
            np.power(radius_e, 2) * np.power(np.cos(latitude), 2)
            + np.power(radius_p, 2) * np.power(np.sin(latitude), 2)
        )
    )
    return radius


def spherical_to_xyz(r, phi, theta, site, re=None, ke=4.0 / 3.0):
    """
    Trasforma le coordinate sferiche (r, phi, theta) in cartesiane
    (x, y, z), centrate sul sito (proiezione aeqd).

    Tiene conto sia dell'accorciarsi della distanza ortodromica con l'aumentare
    dell'angolo di elevazione sia dell'aumento dell'altezza.

    INPUT:
    -r        --np.ndarray               : array dei ranges [m]
    -phi      --np.ndarray               : array degli angoli azimutali in gradi.
    -theta    --Union[np.ndarray, float] : array degli angoli di elevazione in gradi,
                                           con 0° all'orizzonte e +90° la direzione di
                                           puntamento sulla verticale del radar.
    -site    --tuple                     : sequenza di lon, lat, alt del sito radar
    -re      --float = 6371000           : raggio terrestre [m] (default 6371000 m).
    -ke      --Optional[float]=4/3       : fattore di aggiustamento per tener conto
                                           della dipendenza della propagazione del
                                           segnale radar dal gradiente di rifrattività.
                                           Il valore di default 4/3 è una buona approssimazione
                                           per quasi tutte le lunghezze d'onda.
    OUTPUT:
    -xyz     --np.ndarray                : array delle coordinate cartesiane; ha shape (...,3).
    -aeqd    --class:`gdal:osgeo.osr.SpatialReference` :
                                           sistema di riferimento finale (AEQD-Projection).
    """

    centalt = site[2]

    if re is None:
        # if no radius is given, get the approximate radius of the WGS84
        # ellipsoid for the site's latitude
        re = get_earth_radius(site[1])
        # Set up aeqd-projection sitecoord-centered, wgs84 datum and ellipsoid
        # use world azimuthal equidistant projection
        projstr = (
            f"+proj=aeqd +lon_0={site[0]:f} +x_0=0 +y_0=0 "
            f"+lat_0={site[1]:f} +ellps=WGS84 +datum=WGS84 "
            "+units=m +no_defs"
        )
    else:
        # Set up aeqd-projection sitecoord-centered, assuming spherical earth
        # use sphere azimuthal equidistant projection
        projstr = f"+proj=aeqd +lon_0={site[0]:f} +lat_0={site[1]:f} " f"+a={re:f} +b={re:f} +units=m +no_defs"

    try:
        crs = osr.SpatialReference()
        crs.ImportFromProj4(projstr)
        try:
            crs.AutoIdentifyEPSG()
        except RuntimeError:
            pass
        aeqd = crs
    except ModuleNotFoundError:
        aeqd = projstr

    r = np.asanyarray(r)
    theta = np.asanyarray(theta)
    phi = np.asanyarray(phi)

    if r.ndim:
        r = r.reshape((1,) * (3 - r.ndim) + r.shape)

    if phi.ndim:
        phi = phi.reshape((1,) + phi.shape + (1,) * (2 - phi.ndim))

    if not theta.ndim:
        theta = np.broadcast_to(theta, phi.shape)

    dims = 3

    if phi.ndim and theta.ndim and (theta.shape[0] == phi.shape[1]):
        dims -= 1
    if r.ndim and theta.ndim and (theta.shape[0] == r.shape[2]):
        dims -= 1

    if theta.ndim and phi.ndim:
        theta = theta.reshape(theta.shape + (1,) * (dims - theta.ndim))

    z = bin_altitude(r, theta, centalt, re=re, ke=ke)
    dist = site_distance(r, theta, z, re=re, ke=ke)

    if phi.ndim and r.ndim and (r.shape[2] == phi.shape[1]):
        z = np.squeeze(z)
        dist = np.squeeze(dist)
        phi = np.squeeze(phi)

    x = dist * np.cos(np.radians(90 - phi))
    y = dist * np.sin(np.radians(90 - phi))

    if z.ndim:
        z = np.broadcast_to(z, x.shape)

    xyz = np.stack((x, y, z), axis=-1)

    if xyz.ndim == 1:
        xyz.shape = (1,) * 3 + xyz.shape
    elif xyz.ndim == 2:
        xyz.shape = (xyz.shape[0],) + (1,) * 2 + (xyz.shape[1],)

    return xyz, aeqd
