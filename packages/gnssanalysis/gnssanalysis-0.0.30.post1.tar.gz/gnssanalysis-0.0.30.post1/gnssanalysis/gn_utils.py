import logging as _logging
import os as _os
import sys as _sys

import click as _click


def diffutil_verify_input(input):
    #     log_lvl = 40 if atol is None else 30 # 40 is error, 30 is warning. Constant tolerance differences are reported as warnings
    if input is None:
        _click.echo(f"Error: Missing '-i' / '--input' arguments.")
        _sys.exit(-1)
    for i in range(len(input)):
        if (input[i]) is None:
            _click.echo(f"Error: Missing argument {i} of '-i' / '--input'.")
            _sys.exit(-1)
        _click.Path(exists=True)(input[i])
    _logging.info(f":diffutil input1: {_os.path.abspath(input[0])}")
    _logging.info(f":diffutil input2: {_os.path.abspath(input[1])}")


def diffutil_verify_status(status, passthrough):
    if status:
        if not passthrough:
            _logging.error(msg=f":diffutil failed. Calling sys.exit\n")
            _sys.exit(status)
        else:
            _logging.info(msg=f":diffutil failed but no sys.exit as passthrough enabled\n")
    else:
        _logging.info(":diffutil [ALL OK]")


def get_filetype(path):
    """
    Returns a suffix of a file from a path,
    Uses a dict to correct for known suffix issues file types.
    If not present in dict -> return suffix as extracted.
    Also, strips out the underscore-appended part of the suffix, e.g. _smoothed.
    """
    basename = _os.path.basename(path)
    suffix = basename.split(".")[1].lower().partition("_")[0]
    filetype_dict = {"snx": "sinex", "sum": "trace", "eph": "sp3", "inx": "ionex"}
    if suffix in filetype_dict.keys():
        return filetype_dict[suffix]
    elif suffix == "out":
        return basename[:3]
    elif suffix[:2].isdigit and suffix[2] == "i":
        return "ionex"
    return suffix


@_click.group(invoke_without_command=True)
@_click.option(
    "-i",
    "--input",
    nargs=2,
    type=str,
    help="path to compared files, can be compressed with LZW (.Z) or gzip (.gz). Takes exactly two arguments",
)
@_click.option(
    "--passthrough",
    is_flag=True,
    help="return 0 even if failed. Useful for pipeline runs",
)
@_click.option(
    "-a",
    "--atol",
    type=float,
    default=None,
    help="absolute tolerance",
    show_default=True,
)
@_click.option("-c", "--coef", type=float, default=1, help="std coefficient")
@_click.option("-l", "--log_lvl", type=int, default=40, help="logging level selector")
@_click.option(
    "-p",
    "--plot",
    is_flag=True,
    help="produce plotext plot (experimental)",
)
@_click.pass_context
def diffutil(ctx, input, passthrough, atol, coef, log_lvl, plot):
    _logging.getLogger().setLevel(_logging.INFO)
    _logging.info(f":diffutil ========== STARTING DIFFUTIL ==========")
    if not _os.path.exists(input[0]):
        _logging.error(
            f":diffutil '{input[0]}' input not found on disk. Please check inputs or diffex expression"
        )
        ctx.exit(-1)
    if ctx.invoked_subcommand is None:
        if input is None:
            ctx.fail(ctx.get_help())
        filetype = get_filetype(input[0])
        _logging.info(
            f":diffutil invoking '{filetype}' command based on the extension of the first argument of the input"
        )
        ctx.invoke(diffutil.commands.get(filetype, None))  # else return default None
    else:
        _logging.info(f":diffutil invoking {ctx.invoked_subcommand} command")


@diffutil.command()
@_click.pass_context
def trace(ctx):
    from .gn_diffaux import difftrace

    diffutil_verify_input(ctx.parent.params["input"])
    status = difftrace(
        trace1_path=ctx.parent.params["input"][0],
        trace2_path=ctx.parent.params["input"][1],
        tol=ctx.parent.params["atol"],
        std_coeff=ctx.parent.params["coef"],
        log_lvl=ctx.parent.params["log_lvl"],
        plot=ctx.parent.params["plot"],
    )
    diffutil_verify_status(status=status, passthrough=ctx.parent.params["passthrough"])


@diffutil.command()
@_click.pass_context
def sinex(ctx):
    from .gn_diffaux import diffsnx

    diffutil_verify_input(ctx.parent.params["input"])
    status = diffsnx(
        snx1_path=ctx.parent.params["input"][0],
        snx2_path=ctx.parent.params["input"][1],
        tol=ctx.parent.params["atol"],
        std_coeff=ctx.parent.params["coef"],
        log_lvl=ctx.parent.params["log_lvl"],
    )
    diffutil_verify_status(status=status, passthrough=ctx.parent.params["passthrough"])


@diffutil.command()
@_click.pass_context
def ionex(ctx):
    from .gn_diffaux import diffionex

    diffutil_verify_input(ctx.parent.params["input"])
    status = diffionex(
        ionex1_path=ctx.parent.params["input"][0],
        ionex2_path=ctx.parent.params["input"][1],
        tol=ctx.parent.params["atol"],
        std_coeff=ctx.parent.params["coef"],
        log_lvl=ctx.parent.params["log_lvl"],
    )
    diffutil_verify_status(status=status, passthrough=ctx.parent.params["passthrough"])


@diffutil.command()
@_click.pass_context
def stec(ctx):
    from .gn_diffaux import diffstec

    diffutil_verify_input(ctx.parent.params["input"])
    status = diffstec(
        path1=ctx.parent.params["input"][0],
        path2=ctx.parent.params["input"][1],
        tol=ctx.parent.params["atol"],
        std_coeff=ctx.parent.params["coef"],
        log_lvl=ctx.parent.params["log_lvl"],
    )
    diffutil_verify_status(status=status, passthrough=ctx.parent.params["passthrough"])


@diffutil.command()
@_click.pass_context
@_click.option('-n','--norm-type', type=_click.Choice(["daily", "epoch",'both','sv'],case_sensitive=False), default = None, help = "norm-type can be 'daily', 'epoch', 'both' (epoch + daily) or 'sv' (selects an PRN for each constellation to remove the bias). If None - the step is skipped")
@_click.option('-s','--norm-sv', type=str, multiple = True, default = (), help = "norm-sv overrides norm_type with a PRN to use (multiple inputs are allowed through '-s G01 -s E01'. Skipped by default")
def clk(ctx, norm_type, norm_sv):
    from .gn_diffaux import diffclk
    diffutil_verify_input(ctx.parent.params["input"])
    status = diffclk(
        clk_a_path=ctx.parent.params["input"][0],
        clk_b_path=ctx.parent.params["input"][1],
        tol=ctx.parent.params["atol"],
        log_lvl=ctx.parent.params["log_lvl"],
        norm_type=norm_type if norm_sv is () else norm_sv
    )
    diffutil_verify_status(status=status, passthrough=ctx.parent.params["passthrough"])


@diffutil.command()
@_click.pass_context
@_click.option(
    "--aux1",
    type=_click.Path(exists=True),
    default=None,
    help="path to aux1 file",
    show_default=True,
)
@_click.option(
    "--aux2",
    type=_click.Path(exists=True),
    default=None,
    help="path to aux2 file",
    show_default=True,
)
@_click.option(
    "--hlm_mode",
    type=_click.Choice(["ECF", "ECI"], case_sensitive=False),
    help="helmert inversion mode",
    default=None,
    show_default=True,
)
def sp3(ctx, aux1, aux2, hlm_mode):  # no coef
    from .gn_diffaux import diffsp3

    diffutil_verify_input(ctx.parent.params["input"])
    status = diffsp3(
        sp3_a_path=ctx.parent.params["input"][0],
        sp3_b_path=ctx.parent.params["input"][1],
        clk_a_path=aux1,
        clk_b_path=aux2,
        tol=ctx.parent.params["atol"],
        log_lvl=ctx.parent.params["log_lvl"],
        hlm_mode=hlm_mode,
        plot=ctx.parent.params["plot"],
    )
    diffutil_verify_status(status=status, passthrough=ctx.parent.params["passthrough"])


@diffutil.command()
@_click.pass_context
def pod(ctx):  # no coef
    from .gn_diffaux import diffpodout

    diffutil_verify_input(ctx.parent.params["input"])
    status = diffpodout(
        pod_out_a_path=ctx.parent.params["input"][0],
        pod_out_b_path=ctx.parent.params["input"][1],
        tol=ctx.parent.params["atol"],
        log_lvl=ctx.parent.params["log_lvl"],
    )
    diffutil_verify_status(status=status, passthrough=ctx.parent.params["passthrough"])


@diffutil.command()
@_click.pass_context
def blq(ctx):  # no coef
    from .gn_diffaux import diffblq

    diffutil_verify_input(ctx.parent.params["input"])
    status = diffblq(
        blq_a_path=ctx.parent.params["input"][0],
        blq_b_path=ctx.parent.params["input"][1],
        tol=ctx.parent.params["atol"],
        log_lvl=ctx.parent.params["log_lvl"],
    )
    diffutil_verify_status(status=status, passthrough=ctx.parent.params["passthrough"])


@_click.command()
@_click.argument("sinexpaths", required=True, nargs=-1, type=_click.Path(exists=True))
@_click.option("-o", "--outdir", type=_click.Path(exists=True), help="output dir", default=None)
def snxmap(sinexpaths, outdir):
    """Creates sinex station map html. Parses sinex SITE/ID block and create an html map.
    Expects paths to sinex files (.snx/.ssc). Can also be compressed with LZW (.Z)"""
    from gnssanalysis import gn_io as _gn_io, gn_plot as _gn_plot

    size = 0.5
    _logging.getLogger().setLevel(_logging.INFO)
    _logging.info(msg=sinexpaths)
    id_df = _gn_io.sinex.gather_snx_id(sinexpaths, add_markersize=True, size=size)
    _gn_plot.id_df2html(id_df=id_df, outdir=outdir, verbose=True)


@_click.command()
@_click.option("-s", "--sp3paths", required=True, multiple=True, type=_click.Path(exists=True))
@_click.option(
    "-c",
    "--clkpaths",
    required=False,
    multiple=True,
    type=_click.Path(exists=True),
    default=None,
)
@_click.option(
    "-o",
    "--output",
    type=_click.Path(exists=True),
    help="output path",
    default=_os.curdir + "/merge.sp3",
)
def sp3merge(sp3paths, clkpaths, output):
    """
    sp3 files paths to merge, Optional clock files which is useful to insert clk offset values into sp3 file.
    """
    from .gn_io import sp3

    _logging.info(msg=output)
    merged_df = sp3.sp3merge(sp3paths=sp3paths, clkpaths=clkpaths)
    sp3.write_sp3(sp3_df=merged_df, path=output)


@_click.command()
@_click.option("-l", "--logglob", required=True, type=str, help="logs glob path (required)")
@_click.option("-r", "--rnxglob", type=str, help="rinex glob path")
@_click.option("-o", "--output", type=str, help="rinex glob path", default="./metagather.snx")
@_click.option(
    "-fs",
    "--framesnx",
    type=_click.Path(exists=True),
    help="frame sinex path",
    default=None,
)
@_click.option(
    "-fd",
    "--frame_dis",
    type=_click.Path(exists=True),
    help="frame discontinuities file path (required with --frame_snx)",
    default=None,
)
@_click.option(
    "-fp",
    "--frame_psd",
    type=_click.Path(exists=True),
    help="frame psd file path",
    default=None,
)
@_click.option(
    "-d",
    "--datetime",
    help="date to which project frame coordinates, default is today",
    default=None,
)
@_click.option(
    "-n",
    "--num_threads",
    type=int,
    help="number of threads to run in parallel",
    default=None,
)
def log2snx(logglob, rnxglob, outfile, frame_snx, frame_dis, frame_psd, datetime, num_threads):
    """
    IGS log files parsing utility. Globs over log files using LOGGLOB expression
     and outputs SINEX metadata file. If provided with frame and frame discontinuity files (soln),
    will project the selected stations present in the frame to the datetime specified.

    How to get the logfiles:

    rclone sync igs:pub/sitelogs/ /data/station_logs/station_logs_IGS -vv

    How to get the frame files:

    rclone sync itrf:pub/itrf/itrf2014 /data/ITRF/itrf2014/ -vv --include "*{gnss,IGS-TRF}*" --transfers=10

    rclone sync igs:pub/ /data/TRF/ -vv --include "{IGS14,IGb14,IGb08,IGS08}/*"

    see rclone config options inside this script file
    Alternatively, use s3 bucket link to download all the files needed s3://peanpod/aux/

    install rclone with curl https://rclone.org/install.sh | sudo bash -s beta

    rclone config file (content from rclone.conf):

    \b
    [cddis]
    type = ftp
    host = gdc.cddis.eosdis.nasa.gov
    user = anonymous
    pass = somerandomrandompasswordhash
    explicit_tls = true

    \b
    [itrf]
    type = ftp
    host = itrf-ftp.ign.fr
    user = anonymous
    pass = somerandomrandompasswordhash

    \b
    [igs]
    type = ftp
    host = igs-rf.ign.fr
    user = anonymous
    pass = somerandomrandompasswordhash
    """
    from .gn_io import igslog

    if isinstance(rnxglob, list):
        if (len(rnxglob) == 1) & (
            rnxglob[0].find("*") != -1
        ):  # it's rnx_glob expression (may be better to check if star is present)
            rnxglob = rnxglob[0]

    igslog.write_meta_gather_master(
        logs_glob_path=logglob,
        rnx_glob_path=rnxglob,
        out_path=outfile,
        frame_snx_path=frame_snx,
        frame_soln_path=frame_dis,
        frame_psd_path=frame_psd,
        frame_datetime=datetime,
        num_threads=num_threads,
    )


@_click.command()
@_click.argument("trace_paths", nargs=-1, required=True, type=_click.Path(exists=True))
@_click.option("-n", "--name", "db_name", default="trace2mongo", type=str, help="database name")
def trace2mongo(trace_paths, db_name):
    """Support bash wildcards. Could be used as:

    trace2mongo  /data/ginan/examples/ex11/ex11-*.TRACE"""
    from pymongo import MongoClient
    from gnssanalysis import gn_io

    client = MongoClient("localhost", 27017)
    client.drop_database(db_name)
    mydb = client[db_name]
    mydb.create_collection(name="States")
    mydb.create_collection(name="Measurements")

    # db_name = _os.path.basename(trace_path).partition('.')[0]
    for trace_path in trace_paths:
        trace_bytes = gn_io.common.path2bytes(trace_path)

        df_states = gn_io.trace._read_trace_states(trace_bytes)
        df_residuals = gn_io.trace._read_trace_residuals(trace_bytes)

        mydb.States.insert_many(trace.states2eda(df_states))
        mydb.Measurements.insert_many(trace.residuals2eda(df_residuals))
