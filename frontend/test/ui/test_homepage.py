from datetime import datetime
import subprocess

import pytest
import requests

from pages.desktop.home import Home
from pages.desktop.detail import Detail
from pages.desktop.privacy import Privacy
from pages.desktop.terms import Terms
from pages.desktop.about import About


@pytest.mark.nondestructive
def test_copter_loads(base_url, selenium):
    """Test Firefox 'copter' loads on home page"""
    page = Home(selenium, base_url).open()
    assert page.header.is_copter_displayed


@pytest.mark.nondestructive
def test_install_button_loads(base_url, selenium):
    """Test install button for test pilot addon loads"""
    page = Home(selenium, base_url).open()
    assert page.header.is_install_button_displayed


@pytest.mark.nondestructive
def test_number_of_experiments(base_url, selenium):
    """Test current number of experiments"""
    page = Home(selenium, base_url).open()
    url = '{0}/{1}'.format(base_url, 'api/experiments.json')
    # Ping api to get current number of completed experiments
    data = requests.get(url, verify=False).json()
    completed_experiments = len(
        [value for value in data['results'] if 'completed' in value and
         value['completed'] < str(datetime.utcnow())])
    assert len(page.body.experiments) == int(
        len(data['results']) - completed_experiments)


@pytest.mark.nondestructive
def test_experiments_load_correct_pages(base_url, selenium):
    """Test clicking an experiment loads the correct page"""
    page = Home(selenium, base_url).open()
    name = page.body.experiments[0].name
    experiment = page.body.experiments[0].click()
    assert experiment.name in name


@pytest.mark.parametrize('page, title', [
    [Privacy, 'Test Pilot Privacy Notice'],
    [Terms, 'Test Pilot Terms of Use'],
    [About, 'About Test Pilot']])
@pytest.mark.nondestructive
def test_support_pages(base_url, selenium, page, title):
    """Test the support pages load correctly"""
    page = page(selenium, base_url).open()
    assert title in page.title


@pytest.mark.nondestructive
def test_incomplete_email(base_url, selenium):
    """Test signup with incorrect email"""
    page = Home(selenium, base_url).open()
    assert page.signup_footer.is_stay_informed_displayed
    page.signup_footer.sign_up('test')
    assert page.signup_footer.is_stay_informed_displayed


ff = subprocess.Popen("firefox --verison", shell=True, stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT)


@pytest.mark.nondestructive
@pytest.mark.skipif('57' not in ff.stdout.readlines(),
                    reason="57 needed to install unsigned addon")
def test_install_of_test_pilot_addon(
        base_url, selenium, firefox, notifications):
    """Check that the testpilot addon is installable and installs."""
    page = Home(selenium, base_url).open()
    experiments = page.header.click_install_button()
    firefox.browser.wait_for_notification(notifications.AddOnInstallComplete)
    assert 'Welcome to Test Pilot!' in experiments.welcome_popup.title


@pytest.mark.nondestructive
@pytest.mark.skipif('57' not in ff.stdout.readlines(),
                    reason="57 needed to install unsigned addon")
def test_enable_experiment(base_url, selenium, firefox, notifications):
    """Test enabling of an experiment."""
    page = Home(selenium, base_url).open()
    experiments = page.header.click_install_button()
    experiments.welcome_popup.close()
    experiment = experiments.find_experiment(experiment='Dev Example')
    experiment.enable()
    firefox.browser.wait_for_notification(
        notifications.AddOnInstallComplete).close()
    firefox.browser.wait_for_notification(
        notifications.AddOnInstallConfirmation).install()
    firefox.browser.wait_for_notification(
        notifications.AddOnInstallComplete).close()
    assert Detail(selenium, base_url).enabled_popup.is_popup_displayed()
