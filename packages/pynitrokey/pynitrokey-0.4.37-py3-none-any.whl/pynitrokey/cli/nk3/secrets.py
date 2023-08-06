from base64 import b32decode
from typing import Callable, List, Optional

import click

from pynitrokey.cli.nk3 import Context, nk3
from pynitrokey.helpers import AskUser, local_print
from pynitrokey.nk3.secrets_app import (
    STRING_TO_KIND,
    Algorithm,
    SecretsApp,
    SecretsAppException,
    SecretsAppExceptionID,
    SecretsAppHealthCheckException,
)


@nk3.group()
@click.pass_context
def secrets(ctx: click.Context) -> None:
    """Nitrokey Secrets App. Manage OTP secrets on the device.
    Use NITROPY_SECRETS_PASSWORD to pass password for the scripted execution."""
    pass


def repeat_if_pin_needed(func) -> Callable:  # type: ignore[no-untyped-def]
    """
    Decorated function should have at least one argument,
    of which the first one should be an instance of the SecretsApp. Otherwise, a RuntimeError is raised.
    """

    def wrapper(*args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        assert len(args) >= 1 and isinstance(
            args[0], SecretsApp
        ), "repeat_if_pin_needed: SecretsApp should be passed as an argument to this decorator"
        app: SecretsApp = args[0]

        try:
            if app.protocol_v2_confirm_all_requests_with_pin():
                authenticate_if_needed(app)
            func(*args, **kwargs)
        except SecretsAppException as e:
            # Behavior below is for the v3 version of the protocol. Bail if v2 is used.
            if app.protocol_v2_confirm_all_requests_with_pin():
                raise

            if e.to_id() == SecretsAppExceptionID.SecurityStatusNotSatisfied:
                local_print("PIN is required to run this command.")
            elif e.to_id() == SecretsAppExceptionID.NotFound:
                local_print(
                    "Credential not found. Please provide PIN below to search in the PIN-protected database."
                )
            else:
                raise
            # Ask for PIN and retry
            authenticate_if_needed(app)
            func(*args, **kwargs)

    return wrapper


@secrets.command()
@click.pass_obj
@click.argument(
    "name",
    type=click.STRING,
)
@click.argument(
    "secret",
    type=click.STRING,
    # help="The shared secret string (by default in base32)",  # Help can't be enabled on the positional argument
)
@click.option(
    "--digits-str",
    "digits_str",
    type=click.Choice(["6", "8"]),
    help="Digits count",
    default="6",
)
@click.option(
    "--kind",
    "kind",
    type=click.Choice(choices=STRING_TO_KIND.keys(), case_sensitive=False),  # type: ignore[arg-type]
    help="OTP mechanism to use. Case insensitive.",
    default="TOTP",
)
@click.option(
    "--hash",
    "hash",
    type=click.Choice(["SHA1", "SHA256"]),
    help="Hash algorithm to use",
    default="SHA1",
)
@click.option(
    "--counter-start",
    "counter_start",
    type=click.INT,
    help="Starting value for the counter (HOTP only)",
    default=0,
)
@click.option(
    "--touch-button",
    "touch_button",
    type=click.BOOL,
    help="This credential requires button press before use",
    is_flag=True,
)
@click.option(
    "--protect-with-pin",
    "pin_protection",
    type=click.BOOL,
    help="This credential should be additionally encrypted with a PIN, and require it before each use",
    is_flag=True,
)
def register(
    ctx: Context,
    name: str,
    secret: str,
    digits_str: str,
    kind: str,
    hash: str,
    counter_start: int,
    touch_button: bool,
    pin_protection: bool,
) -> None:
    """Register OTP credential.

    Write SECRET under the NAME.
    SECRET should be encoded in base32 format.
    """
    digits = int(digits_str)
    secret_bytes = b32decode(secret)
    otp_kind = STRING_TO_KIND[kind.upper()]
    hash_algorithm = Algorithm.Sha1 if hash == "SHA1" else Algorithm.Sha256
    with ctx.connect_device() as device:
        app = SecretsApp(device)
        ask_to_touch_if_needed()

        @repeat_if_pin_needed
        def call(app: SecretsApp) -> None:
            app.register(
                name.encode(),
                secret_bytes,
                digits,
                kind=otp_kind,
                algo=hash_algorithm,
                initial_counter_value=counter_start,
                touch_button_required=touch_button,
                pin_based_encryption=pin_protection,
            )

        call(app)
        local_print("Done")


def check_experimental_flag(experimental: bool) -> None:
    """Helper function to show common warning for the experimental features"""
    if not experimental:
        local_print(" ")
        local_print(
            "This feature is experimental, which means it was not tested thoroughly.\n"
            "Note: data stored with it can be lost in the next firmware update.\n"
            "Please pass --experimental switch to force running it anyway."
        )
        local_print(" ")
        raise click.Abort()


def ask_to_touch_if_needed() -> None:
    """Helper function to show common request for the touch if device signalizes it"""
    local_print("Please touch the device if it blinks")


@secrets.command()
@click.pass_obj
@click.option(
    "--hex",
    "hex",
    type=click.BOOL,
    help="Use hex representation",
    default=False,
    is_flag=True,
)
def list(ctx: Context, hex: bool) -> None:
    """List registered OTP credentials."""
    with ctx.connect_device() as device:
        app = SecretsApp(device)
        if app.is_pin_healthy():
            local_print(
                "Please provide PIN to show PIN-protected entries (if any), or press ENTER to skip"
            )
            try:
                ask_to_touch_if_needed()
                authenticate_if_needed(app)
            except click.Abort:
                pass
        credentials_list = app.list()
        for e in credentials_list:
            local_print(e.hex() if hex else e)
        if len(credentials_list) == 0:
            local_print("No credentials found")


@secrets.command()
@click.pass_obj
@click.argument(
    "name",
    type=click.STRING,
)
def remove(ctx: Context, name: str) -> None:
    """Remove OTP credential."""
    with ctx.connect_device() as device:
        app = SecretsApp(device)
        ask_to_touch_if_needed()

        @repeat_if_pin_needed
        def call(app: SecretsApp) -> None:
            app.delete(name.encode())

        call(app)
        local_print("Done")


@secrets.command()
@click.pass_obj
@click.option(
    "--force",
    is_flag=True,
    help="Do not ask for confirmation",
)
def reset(ctx: Context, force: bool) -> None:
    """Remove all OTP credentials from the device."""
    confirmed = force or click.confirm("Do you want to continue?")
    if not confirmed:
        raise click.Abort()
    with ctx.connect_device() as device:
        app = SecretsApp(device)
        ask_to_touch_if_needed()
        app.reset()
        local_print("Done")


@secrets.command()
@click.pass_obj
@click.argument(
    "name",
    type=click.STRING,
)
@click.option(
    "--timestamp",
    "timestamp",
    type=click.INT,
    help="The timestamp to use instead of the local time (TOTP only)",
    default=0,
)
@click.option(
    "--period",
    "period",
    type=click.INT,
    help="The period to use in seconds (TOTP only)",
    default=30,
)
def get(
    ctx: Context,
    name: str,
    timestamp: int,
    period: int,
) -> None:
    """Generate OTP code from registered credential."""
    # TODO: for TOTP get the time from a timeserver via NTP, instead of the local clock

    from datetime import datetime

    timestamp = timestamp if timestamp else int(datetime.timestamp(datetime.now()))
    with ctx.connect_device() as device:
        app = SecretsApp(device)
        ask_to_touch_if_needed()

        @repeat_if_pin_needed
        def call(app: SecretsApp) -> None:
            code = app.calculate(name.encode(), timestamp // period)
            local_print(
                f"Timestamp: {datetime.isoformat(datetime.fromtimestamp(timestamp), timespec='seconds')} ({timestamp}), period: {period}"
            )
            local_print(code.decode())

        try:
            call(app)

        except SecretsAppException as e:
            local_print(
                f"Device returns error: {e}. \n"
                f"This credential id might not be registered, or its not allowed to be used here."
            )


@secrets.command()
@click.pass_obj
@click.argument(
    "name",
    type=click.STRING,
)
@click.argument(
    "code",
    type=click.INT,
)
def verify(ctx: Context, name: str, code: int) -> None:
    """Proceed with the incoming OTP code verification (aka reverse HOTP).
    Use the "register" command to create the credential for this action.
    """
    with ctx.connect_device() as device:
        app = SecretsApp(device)
        ask_to_touch_if_needed()

        @repeat_if_pin_needed
        def call(app: SecretsApp) -> None:
            app.verify_code(name.encode(), code)

        try:
            call(app)
        except SecretsAppException as e:
            local_print(
                f"Device returns error: {e}. \n"
                f"This credential id might not be registered, is of wrong type, or the provided HOTP code has not passed verification."
            )


def ask_for_passphrase_if_needed(app: SecretsApp) -> Optional[str]:
    health_check = helper_secrets_app_health_check(app)
    if health_check:
        local_print(*health_check)
    if not app.is_pin_healthy():
        raise SecretsAppHealthCheckException("PIN not available to use")
    passphrase = AskUser(
        f"Current PIN ({app.select().pin_attempt_counter} attempts left)",
        envvar="NITROPY_SECRETS_PASSWORD",
        hide_input=True,
    ).ask()
    return passphrase


def authenticate_if_needed(app: SecretsApp) -> None:
    try:
        passphrase = ask_for_passphrase_if_needed(app)
        if passphrase:
            ask_to_touch_if_needed()
            app.verify_pin_raw(passphrase)
        else:
            local_print("No PIN provided")
    except SecretsAppHealthCheckException:
        raise click.Abort()
    except Exception as e:
        local_print(
            f'Authentication failed with error: "{e}" \n'
            "Please make sure the provided PIN is correct."
        )
        raise click.Abort()


@secrets.command()
@click.pass_obj
@click.password_option()
def set_pin(ctx: Context, password: str) -> None:
    """Set or change the PIN used to authenticate to other commands."""
    new_password = password

    with ctx.connect_device() as device:
        try:
            app = SecretsApp(device)
            ask_to_touch_if_needed()

            if app.select().pin_attempt_counter is None:
                app.set_pin_raw(new_password)
                local_print("Password set")
                return

            current_password = ask_for_passphrase_if_needed(app)
            if current_password is None:
                raise click.Abort()
            app.change_pin_raw(current_password, new_password)
            local_print("Password changed")
        except SecretsAppException as e:
            local_print(
                f"Device returns error: {e}. \n" f"The new or current PIN is invalid."
            )


@secrets.command()
@click.pass_obj
def status(ctx: Context) -> None:
    """Show application status"""
    with ctx.connect_device() as device:
        app = SecretsApp(device)
        r = app.select()
        local_print(f"{r}")
        local_print(*helper_secrets_app_health_check(app))


def helper_secrets_app_health_check(app: SecretsApp) -> List[str]:
    messages = []
    r = app.select()
    if r.pin_attempt_counter is None:
        messages.append(
            "- Application does not have a PIN. Set PIN before the first use."
        )
    if r.pin_attempt_counter == 0:
        messages.append(
            "- All attempts on the PIN counter are used. Call factory reset to use the PIN feature of the secrets application again."
        )
    if (
        app.feature_challenge_response_support()
        or app.feature_old_application_version()
    ):
        messages.append("- This application version is outdated.")

    if messages:
        messages.insert(0, "Health check notes:")
    return messages
