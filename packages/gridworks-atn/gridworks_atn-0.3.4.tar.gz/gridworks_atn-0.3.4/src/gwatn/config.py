"""Settings for an AtomicTNode, readable from environment and/or from env files."""

from typing import Optional

import pendulum
from gridworks.gw_config import AlgoApiSecrets
from gridworks.gw_config import GNodeSettings
from gridworks.gw_config import Public
from pydantic import BaseSettings
from pydantic import SecretStr


class AtnSettings(GNodeSettings):
    g_node_alias: str = "d1.isone.ver.keene.holly"
    g_node_role_value: str = "AtomicTNode"
    my_super_alias: str = "d1.isone.ver.keene.super1"
    g_node_id: str = "6bb37cc5-740d-40f5-a535-43987a5d07b4"
    g_node_instance_id: str = "00000000-0000-0000-0000-000000000000"
    scada_gni_id: Optional[str] = None
    sk: SecretStr = SecretStr(
        "K6iB3AHmzSQ8wDE91QdUfaheDMEtf2WJUMYeeRptKxHiTxG3HC+iKpngXmi82y2r9uVPYwTI5aGiMhdXmPRxcQ=="
    )
    # Public address 4JHRDNY4F6RCVGPALZULZWZNVP3OKT3DATEOLINCGILVPGHUOFY7KCHVIQ

    # Next 4 settings are consistent with dev env settings in gridworks-marketmaker repo
    market_maker_alias = "d1.isone.ver.keene"
    market_maker_algo_address = (
        "CYWMWYHJ7ON4IR5XQDJBBPDU472QU4KJQ6XQVZBIIRTCHT6SHTFNHEAVC4"
    )
    mm_api_root = "http://localhost:7997"
    initial_time_unix_s = pendulum.datetime(
        year=2020, month=1, day=1, hour=4, minute=20
    ).int_timestamp

    class Config:
        env_prefix = "ATN_"
        env_nested_delimiter = "__"


class ValidatorSettings(BaseSettings):
    algo_api_secrets: AlgoApiSecrets = AlgoApiSecrets()
    public: Public = Public()
    sk: SecretStr = SecretStr(
        "FCLmrvflibLD6Deu3NNiUQCC9LOWpXLsbMR/cP2oJzH8IT4Zu8vBAhRNsXoWF+2i6q2KyBZrPhmbDCKJD7rBBg=="
    )
    cert_name: str = "Molly Metermaid"
    name: str = "Molly Inc Telemetry Surveyors and Purveyors"
    api_root: str = "http://localhost:8001"

    class Config:
        env_prefix = "VLDTR_"
        env_nested_delimiter = "__"


class TaOwnerSettings(BaseSettings):
    algo_api_secrets: AlgoApiSecrets = AlgoApiSecrets()
    public: Public = Public()
    sk: SecretStr = SecretStr(
        "sp4SDWmH8Rin0IhPJQq1UMsSR5C0j1IGqzLdcwCMySBVzT8lEUwjwwpS9z6l6dKSg52WWEjRdJDAL+eVt4kvBg=="
    )

    ta_daemon_addr: str = "NZXUSTZACPVJBHRSSJ5KE3JUPCITK5P2O4FE67NYPXRDVCJA6ZX4AL62EA"
    ta_validator_addr: str = (
        "7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII"
    )
    ta_validator_api_root: str = "http://localhost:8001"
    ta_daemon_api_fqdn: str = "http://localhost"
    ta_daemon_api_port: str = "8002"
    initial_ta_alias: str = "d1.isone.ver.keene.holly.ta"
    micro_lat: int = 45511230
    micro_lon: int = -68354650

    class Config:
        env_prefix = "HH_"
        env_nested_delimiter = "__"


class TaDaemonSettings(BaseSettings):
    algo_api_secrets: AlgoApiSecrets = AlgoApiSecrets()
    public: Public = Public()
    sk: SecretStr = SecretStr(
        "tQ8ABbLLR96cnRE3Y2tlrj2d/rNPRFkf8FosJ46tVIlub0lPIBPqkJ4yknqibTR4kTV1+ncKT324feI6iSD2bw=="
    )
    ta_owner_addr: str = "KXGT6JIRJQR4GCSS647KL2OSSKBZ3FSYJDIXJEGAF7TZLN4JF4DGDDX4BI"
    validator_addr: str = "7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII"

    class Config:
        env_prefix = "TAD_"
        env_nested_delimiter = "__"


class ScadaSettings(GNodeSettings):
    cert_type_value: str = "ASA"
    g_node_alias: str = "d1.isone.ver.keene.holly.scada"
    g_node_role_value: str = "Scada"
    my_super_alias: str = "d1.super1"
    g_node_id: str = "282b2121-ec42-44e0-99fe-d77c40f64ac0"
    g_node_instance_id: str = "b6eab35e-ff90-4380-a5c9-08cf26aaf45e"
    atn_gni_id: Optional[str] = None
    # Next 4 settings are consistent with dev env settings in gridworks-marketmaker repo
    sk: SecretStr = SecretStr(
        "7RaOTVzqiL5NHarfkp7FpR1rjmn3T4Nibd+017Uhd9GpOVe2and91D46zJxO1wycU02TXxVu18cmslBEKgb8IA=="
    )
    # addr "MWKXTOQU3MQXCMJEIYD5PJGIR2RJNEUDVFIHLY75XZ5PJSY2H73W4DPHTM"
    initial_time_unix_s = pendulum.datetime(
        year=2020, month=1, day=1, hour=4, minute=20
    ).int_timestamp

    class Config:
        env_prefix = "SCADA_"
        env_nested_delimiter = "__"


class DiscovererSettings(BaseSettings):
    algo_api_secrets: AlgoApiSecrets = AlgoApiSecrets()
    public: Public = Public()
    sk: SecretStr = SecretStr(
        "X20eXB/VZilEmzaPCDSn9WsuGZ5/f0+IxuEhfYfVtmZR9q5bcbjpBodPpiUCCkr0Xv11sKYxf08PnAKQFNtW3Q=="
    )
    discovered_ctn_alias = "d1.isone.ver.keene.pwrs"
    original_child_alias_list = ["d1.isone.ver.keene.holly"]
    micro_lat = 44838681
    micro_lon = -68705311

    class Config:
        env_prefix = "DISC_"
        env_nested_delimiter = "__"
