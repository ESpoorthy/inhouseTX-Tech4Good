from pathlib import Path


def test_frontend_shell_and_redesign_assets_are_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"InHouseTX" in response.data
    assert b"/static/src/styles.css" in response.data
    assert b"/static/vanilla.js" in response.data

    css = client.get("/static/src/styles.css")
    js = client.get("/static/vanilla.js")
    assert css.status_code == 200
    assert js.status_code == 200
    assert b"InHouseTX redesign system" in css.data
    assert b"feedback-form" in js.data
    assert b"prompt('Correct category" not in js.data
