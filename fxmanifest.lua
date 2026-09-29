fx_version 'cerulean'
game 'gta5'
lua54 'yes'

name 'fivem-graphics-mod'
author 'fivem-graphics-mod'
description 'Visual realista em duas versões: Quality e Performance.'
version '1.0.0'

shared_scripts {
    'shared/config.lua',
    'shared/profiles.lua',
    'shared/timecycle.lua',
    'shared/visual_settings.lua',
}

client_scripts {
    'client/visuals.lua',
    'client/screen.lua',
    'client/main.lua',
}

server_scripts {
    'server/main.lua',
}

ui_page 'nui/index.html'

files {
    'nui/index.html',
    'nui/style.css',
    'nui/app.js',
    'timecycle/quality.xml',
    'timecycle/performance.xml',
}

data_file 'TIMECYCLEMOD_FILE' 'timecycle/quality.xml'
data_file 'TIMECYCLEMOD_FILE' 'timecycle/performance.xml'
