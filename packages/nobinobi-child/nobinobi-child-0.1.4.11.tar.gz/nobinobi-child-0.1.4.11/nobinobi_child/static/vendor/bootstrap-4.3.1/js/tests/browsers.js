/*
 * Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

/* eslint-env node */
/* eslint-disable camelcase */

const browsers = {
  safariMac: {
    base: 'BrowserStack',
    os: 'OS X',
    os_version: 'High Sierra',
    browser: 'Safari',
    browser_version: 'latest'
  },
  chromeMac: {
    base: 'BrowserStack',
    os: 'OS X',
    os_version: 'High Sierra',
    browser : 'Chrome',
    browser_version : 'latest'
  },
  firefoxMac: {
    base: 'BrowserStack',
    os: 'OS X',
    os_version: 'High Sierra',
    browser: 'Firefox',
    browser_version: 'latest'
  },
  edgeWin10: {
    base: 'BrowserStack',
    os: 'Windows',
    os_version: '10',
    browser: 'Edge',
    browser_version: 'latest'
  },
  ie11Win10: {
    base: 'BrowserStack',
    os: 'Windows',
    os_version: '10',
    browser: 'IE',
    browser_version: '11.0'
  },
  chromeWin10: {
    base: 'BrowserStack',
    os: 'Windows',
    os_version: '10',
    browser: 'Chrome',
    browser_version: 'latest'
  },
  firefoxWin10: {
    base: 'BrowserStack',
    os: 'Windows',
    os_version: '10',
    browser: 'Firefox',
    browser_version: 'latest'
  },
  ie10Win8: {
    base: 'BrowserStack',
    os: 'Windows',
    os_version: '8',
    browser: 'IE',
    browser_version: '10.0'
  },
  iphoneX: {
    base: 'BrowserStack',
    os: 'ios',
    os_version: '11.0',
    device: 'iPhone X',
    real_mobile: true
  },
  pixel2: {
    base: 'BrowserStack',
    os: 'android',
    os_version: '8.0',
    device: 'Google Pixel 2',
    real_mobile: true
  }
}

const browsersKeys = Object.keys(browsers)

module.exports = {
  browsers,
  browsersKeys
}
