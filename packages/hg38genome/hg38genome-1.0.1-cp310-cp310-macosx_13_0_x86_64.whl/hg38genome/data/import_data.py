import os


data_catalog = {"exons.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/exons.parquet",
                "genes.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/genes.parquet",
                "CDS.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/CDS.parquet",
                "start_codons.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/start_codons.parquet",
                "stop_codons.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/stop_codons.parquet",
                "transcripts.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/transcripts.parquet",
                "UTR.bed.gz": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/UTR.parquet",
                "Top1000sites_TF.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/Top1000sites_TF.parquet",
                "hg19_CpGs.h5": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/hg19_CpGs.h5",
                "bin100000_bias.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/bin100000_bias.parquet",
                "bin1000000_bias.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/bin1000000_bias.parquet",
                "CpG_islands.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/CpG_islands.parquet",
                "CTCF.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/CTCF.parquet",
                "blacklist_v2.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/blacklist_v2.parquet",
                "hg19_repeats.parquet": "https://raw.githubusercontent.com/kylessmith/hg19genome/master/data/hg19_repeats.parquet",
                }
data_size = {"exons.parquet": "4.8MB",
                "genes.parquet": "1MB",
                "CDS.parquet": "3MB",
                "start_codons.parquet": "0.582MB",
                "stop_codons.parquet": "0.657MB",
                "transcripts.parquet": "2.1MB",
                "UTR.parquet": "2.1MB",
                "Top1000sites_TF.parquet": "3.5MB",
                "hg19_CpGs.h5": "56.3MB",
                "bin100000_bias.parquet": "0.378MB",
                "bin1000000_bias.parquet": "0.06MB",
                "CpG_islands.parquet": "0.667MB",
                "CTCF.parquet": "3.2MB",
                "blacklist_v2.parquet": "0.015MB",
                "hg19_repeats.parquet": "35.4MB",
                }


def download_genome():
    """
    Download the hg38 genome (2bit version) from UCSC
    """
    from os.path import join
    import os

    import requests
    import shutil
    from tqdm.auto import tqdm

    name = "hg38"
    mode = "http"
    urlpath = "%s://hgdownload.cse.ucsc.edu/goldenPath/%s/bigZips/%s.2bit" % \
            (mode, name, name)
    #destdir = os.path.join(os.path.split(os.path.realpath(__file__))[0], "data")
    destdir = os.path.split(os.path.realpath(__file__))[0]
    #remotefile = urlopen(urlpath)
    
    # make an HTTP request within a context manager
    with requests.get(urlpath, stream=True) as r:
        
        # check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length"))
        
        # implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="")as raw:
        
            # save the output to a file
            with open(join(destdir, "%s.2bit" % name), 'wb') as output:
                shutil.copyfileobj(raw, output)


def download_file(filename: str):
    """
    Download a file from the data catalog

    Parameters
    ----------
        filename : str
            Name of the file to download

    Returns
    -------
        None
    """

    from os.path import join
    import os

    import requests
    import shutil
    from tqdm.auto import tqdm

    urlpath = data_catalog[filename]
    destdir = os.path.split(os.path.realpath(__file__))[0]

    # make an HTTP request within a context manager
    with requests.get(urlpath, stream=True) as r:
        
        # check header to get content length, in bytes
        total_length = int(r.headers.get("Content-Length"))
        
        # implement progress bar via tqdm
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="")as raw:
        
            # save the output to a file
            with open(join(destdir, filename), 'wb') as output:
                shutil.copyfileobj(raw, output)


def get_data_file(filename):
    """
    """

    # Find data directory
    data_dir = os.path.split(os.path.realpath(__file__))[0]
    data_dir = os.path.join(data_dir, filename)

    # Check if file exists
    if os.path.exists(data_dir) == False:
        if filename == "hg38.2bit":
            response = input("Would you like to download hg38.2bit (~800MB). [Yes/No]")

            if response.upper() == "YES" or response.upper() == "Y":
                download_genome()
            else:
                raise FileExistsError("Data file does not exist! ("+data_dir+")")
                
        else:
            if filename in data_catalog:
                response = input("Would you like to download " + filename + " (" + data_size[filename] + "). [Yes/No]")

                if response.upper() == "YES" or response.upper() == "Y":
                    download_file()
                else:
                    raise FileExistsError("Data file does not exist! ("+data_dir+")")
            else:
                raise FileExistsError("Data file does not exist! ("+data_dir+")")

    return data_dir


def bulk_download():
    """
    Download all files in the data catalog
    """

    for filename in data_catalog:
        download_file(filename)


def get_data_dir():
    """
    """

    data_dir = os.path.split(os.path.realpath(__file__))[0]

    return data_dir