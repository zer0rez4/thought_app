def assert_tokens(data):
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"


def assert_resend_email_tokens(send_mock):
    first_token = (
        send_mock
        .await_args_list[0]
        .kwargs["token"]
    )

    second_token = (
        send_mock
        .await_args_list[1]
        .kwargs["token"]
    )

    assert first_token != second_token