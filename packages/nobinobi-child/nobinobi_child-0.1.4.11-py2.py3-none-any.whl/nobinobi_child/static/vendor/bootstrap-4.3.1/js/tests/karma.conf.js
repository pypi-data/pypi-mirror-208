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
/* eslint no-process-env: 0 */

const path = require('path')
const ip = require('ip')
const {
  browsers,
  browsersKeys
} = require('./browsers')

const jqueryFile = process.env.USE_OLD_JQUERY ? 'https://code.jquery.com/jquery-1.9.1.min.js' : 'node_modules/jquery/dist/jquery.slim.min.js'
const bundle = process.env.BUNDLE === 'true'
const browserStack = process.env.BROWSER === 'true'

const frameworks = [
  'qunit',
  'sinon'
]

const plugins = [
  'karma-qunit',
  'karma-sinon'
]

const reporters = ['dots']

const detectBrowsers = {
  usePhantomJS: false,
  postDetection(availableBrowser) {
    if (typeof process.env.TRAVIS_JOB_ID !== 'undefined' || availableBrowser.includes('Chrome')) {
      return ['ChromeHeadless']
    }

    if (availableBrowser.includes('Firefox')) {
      return ['FirefoxHeadless']
    }

    throw new Error('Please install Firefox or Chrome')
  }
}

const customLaunchers = {
  FirefoxHeadless: {
    base: 'Firefox',
    flags: ['-headless']
  }
}

let files = [
  'node_modules/popper.js/dist/umd/popper.min.js',
  'node_modules/hammer-simulator/index.js'
]

const conf = {
  basePath: '../..',
  port: 9876,
  colors: true,
  autoWatch: false,
  singleRun: true,
  concurrency: Infinity,
  client: {
    qunit: {
      showUI: true
    }
  }
}

if (bundle) {
  frameworks.push('detectBrowsers')
  plugins.push(
    'karma-chrome-launcher',
    'karma-firefox-launcher',
    'karma-detect-browsers'
  )
  conf.customLaunchers = customLaunchers
  conf.detectBrowsers = detectBrowsers
  files = files.concat([
    jqueryFile,
    'dist/js/bootstrap.js'
  ])
} else if (browserStack) {
  conf.hostname = ip.address()
  conf.browserStack = {
    username: process.env.BROWSER_STACK_USERNAME,
    accessKey: process.env.BROWSER_STACK_ACCESS_KEY,
    build: `bootstrap-${new Date().toISOString()}`,
    project: 'Bootstrap',
    retryLimit: 2
  }
  plugins.push('karma-browserstack-launcher')
  conf.customLaunchers = browsers
  conf.browsers = browsersKeys
  reporters.push('BrowserStack')
  files = files.concat([
    'node_modules/jquery/dist/jquery.slim.min.js',
    'js/dist/util.js',
    'js/dist/tooltip.js',
    'js/dist/!(util|index|tooltip).js' // include all of our js/dist files except util.js, index.js and tooltip.js
  ])
} else {
  frameworks.push('detectBrowsers')
  plugins.push(
    'karma-chrome-launcher',
    'karma-firefox-launcher',
    'karma-detect-browsers',
    'karma-coverage-istanbul-reporter'
  )
  files = files.concat([
    jqueryFile,
    'js/coverage/dist/util.js',
    'js/coverage/dist/tooltip.js',
    'js/coverage/dist/!(util|index|tooltip).js' // include all of our js/dist files except util.js, index.js and tooltip.js
  ])
  reporters.push('coverage-istanbul')
  conf.customLaunchers = customLaunchers
  conf.detectBrowsers = detectBrowsers
  conf.coverageIstanbulReporter = {
    dir: path.resolve(__dirname, '../coverage/'),
    reports: ['lcov', 'text-summary'],
    thresholds: {
      emitWarning: false,
      global: {
        statements: 90,
        branches: 86,
        functions: 89,
        lines: 90
      }
    }
  }
}

files.push('js/tests/unit/*.js')

conf.frameworks = frameworks
conf.plugins = plugins
conf.reporters = reporters
conf.files = files

module.exports = (karmaConfig) => {
  // possible values: karmaConfig.LOG_DISABLE || karmaConfig.LOG_ERROR || karmaConfig.LOG_WARN || karmaConfig.LOG_INFO || karmaConfig.LOG_DEBUG
  conf.logLevel = karmaConfig.LOG_ERROR || karmaConfig.LOG_WARN
  karmaConfig.set(conf)
}
