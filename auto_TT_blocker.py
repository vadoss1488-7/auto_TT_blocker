from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright
from time import sleep
from os import listdir
from PySimpleGUI import popup, popup_error
import logging
import random
import string
import platform
import socket
import uuid
from faker import Faker
from stegano import lsb

class Data:
    def __init__(self, links:str, login:str):
        log_format = '%(asctime)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_handler_all = logging.FileHandler('logs/all_logs.log')
        file_handler_all.setLevel(logging.DEBUG)
        file_handler_all.setFormatter(logging.Formatter(log_format, date_format))

        file_handler_warning = logging.FileHandler('logs/warning_logs.log')
        file_handler_warning.setLevel(logging.WARNING)
        file_handler_warning.setFormatter(logging.Formatter(log_format, date_format))

        file_handler_info = logging.FileHandler('logs/info_logs.log')
        file_handler_info.setLevel(logging.INFO)
        file_handler_info.setFormatter(logging.Formatter(log_format, date_format))

        logger.addHandler(file_handler_all)
        logger.addHandler(file_handler_warning)
        logger.addHandler(file_handler_info)

        self.logger = logger

        try:
            with open(links, 'r', encoding='utf-8') as f:
                self.links = [i.split(' ')[1].strip() for i in f.readlines()]
            with open(login, 'r', encoding='utf-8') as f:
                self.login = [line.strip() for line in f if line.strip()]
        except Exception:
            self.logger.warning('error with files links.txt or login.txt')
            popup_error('error with files links.txt or login.txt')

    def get_system_info(self):
        system_info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "OS Release": platform.release(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Architecture": platform.architecture()[0],
            "Hostname": socket.gethostname(),
            "MAC Address": self.get_mac_address(),
        }
        return system_info

    def get_mac_address(self):
        mac = uuid.getnode()
        mac_address = ':'.join(f"{(mac >> i) & 0xff:02x}" for i in range(0, 48, 8)[::-1])
        return mac_address

    def main(self):
        print("=== Информация о системе ===")
        system_info = self.get_system_info()
        for key, value in system_info.items():
            print(f"{key}: {value}")

    def stegono_data(self):
        all_data = list()
        all_data.append("=== system data ===")
        system_info = self.get_system_info()
        for key, value in system_info.items():
            all_data.append(f"{key}: {value}")
        return '\n'.join(all_data)

class Browser_init:
    def __init__(self):
        self.data = Data('data/links.txt', 'data/login.txt')
        self.links = self.data.links
        self.login = self.data.login
        self.logger = self.data.logger
        try:
            self.stegono_data = self.data.stegono_data()
        except Exception:
            self.logger.warning('stegono data warning')

    def random_string(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_random_cookies(self):
        fake = Faker()
        cookies = []
        for _ in range(5):
            cookie = {
                'name': self.random_string(8),
                'value': self.random_string(16),
                'domain': fake.domain_name(),
                'path': '/',
                'expires': random.randint(1672531199, 2555299200),
                'httpOnly': random.choice([True, False]),
                'secure': random.choice([True, False]),
            }
            cookies.append(cookie)
        return cookies

    def get_random_user_agent(self):
        ua = UserAgent()
        return ua.random

    def start_session(self, p, account_index: int):
        """
        Стартует свежий браузер, создаёт новый контекст (новый UA, случайные cookies),
        открывает страницу и проходит авторизацию под логином с индексом account_index.
        Возвращает (browser, context, page).
        """
        self.logger.info(f'starting fresh browser with new context for account #{account_index+1}')
        browser = p.chromium.launch(headless=False, args=["--incognito"])
        context = browser.new_context(user_agent=self.get_random_user_agent())
        context.add_cookies(self.generate_random_cookies())
        page = context.new_page()
        page.set_default_timeout(60000)

        for attempt in range(3):
            if self.logining(page, account_index) == 1:
                self.logger.info('login success')
                return browser, context, page
            self.logger.warning(f'login attempt {attempt+1} failed, retrying...')
            sleep(2)

        try:
            context.close()
        finally:
            browser.close()
        raise RuntimeError('cannot login after 3 attempts')

    def browser(self):
        if not self.login:
            self.logger.error('no accounts loaded from login.txt')
            return

        with sync_playwright() as p:
            for acc_idx in range(len(self.login)):
                try:
                    browser, context, page = self.start_session(p, acc_idx)

                    popup('CLICK WHILE CAPCHA IS ACCEPT')

                    page.wait_for_load_state('networkidle')

                    for link in self.links:
                        self.block(page, link)

                    self.logger.info(f'session for account #{acc_idx+1} finished, closing browser...')
                    try:
                        context.close()
                    finally:
                        browser.close()

                except Exception as e:
                    self.logger.critical(f'account #{acc_idx+1} failed with error: {e}')

            self.logger.info('all accounts processed; exiting program.')

    def block(self, page, link):
        self.logger.info('block')
        try:
            counter = len(listdir('screenshots'))
            page.goto(link)
            self.logger.debug('load page to complaint')
            page.wait_for_load_state('networkidle')
            self.logger.debug('page loaded')
            try:
                page.evaluate('document.querySelector("#main-content-others_homepage > div > div.e1457k4r14.css-cooqqt-DivShareLayoutHeader-StyledDivShareLayoutHeaderV2-CreatorPageHeader.e13xij562 > div.css-1o9t6sm-DivShareTitleContainer-CreatorPageHeaderShareContainer.e1457k4r15 > div.css-12aeehi-DivButtonPanelWrapper.efrkfhz0 > button:nth-child(4)").click()')
            except Exception:
                sleep(3)
                page.evaluate('document.querySelector("#main-content-others_homepage > div > div.e1457k4r14.css-cooqqt-DivShareLayoutHeader-StyledDivShareLayoutHeaderV2-CreatorPageHeader.e13xij562 > div.css-1o9t6sm-DivShareTitleContainer-CreatorPageHeaderShareContainer.e1457k4r15 > div.css-12aeehi-DivButtonPanelWrapper.efrkfhz0 > button:nth-child(4)").click()')
            self.logger.debug('click to menu')
            sleep(2)
            for i in range(1, 100):
                try:
                    page.evaluate(f'document.querySelector("#floating-ui-{i} > div > div > div:nth-child(1)").click()')
                    break
                except Exception:
                    pass
            self.logger.debug('click to complaint')
            sleep(1)
            try:
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1xsnrje-DivRadioWrapper.ezqf9p66 > label").click()')
            except Exception:
                sleep(3)
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1xsnrje-DivRadioWrapper.ezqf9p66 > label").click()')
            self.logger.debug('click to complaint of account')
            sleep(1)
            try:
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1xsnrje-DivRadioWrapper.ezqf9p66 > label:nth-child(2)").click()')
            except Exception:
                sleep(3)
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1xsnrje-DivRadioWrapper.ezqf9p66 > label:nth-child(2)").click()')
            self.logger.debug('click to complaint situation 1')
            sleep(0.5)
            try:
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1xsnrje-DivRadioWrapper.ezqf9p66 > label:nth-child(3)").click()')
            except Exception:
                sleep(3)
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1xsnrje-DivRadioWrapper.ezqf9p66 > label:nth-child(3)").click()')
            self.logger.debug('click to complaint situation 2')
            sleep(0.5)
            try:
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1xsnrje-DivRadioWrapper.ezqf9p66 > label:nth-child(2)").click()')
            except Exception:
                sleep(3)
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1xsnrje-DivRadioWrapper.ezqf9p66 > label:nth-child(2)").click()')
            self.logger.debug('click to complaint situation 3')
            sleep(0.5)
            try:
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1yswmgr-DivRadioWrapper-DivSubmitWrapper.ezqf9p67 > div.css-1dgbp7a-DivFooter.ezqf9p618 > button").click()')
            except Exception:
                sleep(3)
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > form > div.css-1yswmgr-DivRadioWrapper-DivSubmitWrapper.ezqf9p67 > div.css-1dgbp7a-DivFooter.ezqf9p618 > button").click()')
            self.logger.debug('click to accept complaint')
            sleep(1)
            page.screenshot(path=f'screenshots/screenshot_{counter+1}.png')
            lsb.hide(f'screenshots/screenshot_{counter+1}.png', self.stegono_data).save(f'screenshots/screenshot_{counter+1}.png')
            self.logger.info(f'screenshots/screenshot_{counter+1}.png')
            try:
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > div > div > button").click()')
            except Exception:
                sleep(3)
                page.evaluate('document.querySelector("#tux-portal-container > div > div:nth-child(2) > div > div > div.css-17s26nl-ModalContentContainer.e1wuf0b31 > div > div > section > div > div > button").click()')
            self.logger.info('click to accept')
        except Exception:
            if page.locator('div[class*="cap-flex cap-w-full cap-mt-6 cap-mb-4"]'):
                self.logger.warning('capcha')
                popup('капча')
                self.logger.warning('accept capcha')
            self.logger.warning('error block')

    def logining(self, page, counter):
        try:
            self.logger.info('start logining')
            page.goto('https://www.tiktok.com/explore')
            self.logger.debug('load page')
            page.wait_for_load_state('networkidle')
            sleep(3)
            self.logger.debug('page loaded')
            page.evaluate("document.querySelector('#header-login-button').click()")
            self.logger.debug('click to button login')
            sleep(3)
            page.evaluate('document.querySelector("#loginContainer > div > div > div > div:nth-child(2) > div.css-17hparj-DivBoxContainer.e1cgu1qo0").click()')
            self.logger.debug('click login by phone')
            sleep(3)
            page.evaluate('document.querySelector("#loginContainer > div > form > div.css-1usm4ad-DivDescription.e1521l5b3 > a").click()')
            self.logger.debug('click login by password')
            sleep(3)
            page.fill('#loginContainer > div.css-aa97el-DivLoginContainer.exd0a430 > form > div.css-q83gm2-DivInputContainer.etcs7ny0 > input', self.login[counter].split(':')[0])
            page.fill('#loginContainer > div.css-aa97el-DivLoginContainer.exd0a430 > form > div.css-15iauzg-DivContainer.e1bi0g3c0 > div > input', self.login[counter].split(':')[1])
            sleep(5)
            page.evaluate('document.querySelector("#loginContainer > div.css-aa97el-DivLoginContainer.exd0a430 > form > button").click()')
            self.logger.debug('click to login')
            sleep(5)
            self.logger.info('accept')
            return 1
        except Exception:
            self.logger.warning('error logining')

if __name__ == '__main__':
    Browser_init().browser()
