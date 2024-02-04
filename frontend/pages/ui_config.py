from nicegui import ui

ui.select.default_props('outlined')
ui.input.default_props('dense outlined')


class ui_scr_input(ui.input):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ui_tar_input(ui.input):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


ui_scr_input.default_props('bg-color=grey-10').default_style('height: 15px')
ui_tar_input.default_props('bg-color=blue-grey-10').default_style('height: 39px')

LEN = 1


class COLORS:
    PRIMARY = '#409696'  # 5898D4 #80C8C8
    SECONDARY = '#5A96E0'  # 26A69A
    ACCENT = '#9632C0'  # 9C27B0
    DARK = '#1D1D1D'  # 1D1D1D
    POSITIVE = '#20C040'  # 21BA45
    NEGATIVE = '#C00020'  # C10015
    INFO = '#32C0E0'  # 31CCEC
    WARNING = '#FFFF40'  # F2C037


class HTML:
    RESIZE = '''
        <script>
        function emitSize() {
            emitEvent('resize', {
                width: document.body.offsetWidth,
                height: document.body.offsetHeight,
            });
        }
        window.onload = emitSize;
        window.onresize = emitSize;
        </script>
    '''
    FLEX_GROW = '<style>.q-textarea.flex-grow .q-field__control{height: 100%}</style>'
    HEADER_COLOR = '<style>.q-table.header-color .q-table__top, thead tr:first-child th {background-color: #409696}</style>'
    HEADER_STICKY = '<style>.q-table.sticky .q-table__top, thead tr th{position: sticky z-index: 1}</style>'


class TABLE:
    HEADER = '''
        <q-tr :props="props">
            <q-th v-for="col in props.cols" :key="col.field" :props="props">
                {{ col.label }}
            </q-th>
            <q-th auto-width>
                <q-btn size="12px" color="primary" dense round icon="add" :props="props"
                @click="() => $parent.$emit('_add_row')">
            </q-th>
        </q-tr>
    '''

    BODY = '''
        <q-tr :props="props">
            <q-td key="key" :props="props">
                {{ props.row.key }}
                <q-popup-edit v-model="props.row.key" v-slot="scope"
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)">
                    <q-input v-model="scope.value" dense borderless autofocus @keyup.enter="scope.set"/>
                </q-popup-edit>
            </q-td>
            <q-td key="val" :props="props">
                {{ props.row.val }}
                <q-popup-edit v-model="props.row.val" v-slot="scope"
                    @update:model-value="() => $parent.$emit('_upd_row', props.row)">
                    <q-input v-model="scope.value" dense borderless autofocus @keyup.enter="scope.set"/>
                </q-popup-edit>
            </q-td>
            <q-td auto-width>
                <div class="col">
                    <q-btn size="8px" color="primary" dense round icon="remove" :props="props"
                    @click="() => $parent.$emit('_del_row', props.row)">
                </div>
                <div class="col">
                    <q-btn size="8px" color="primary" dense round icon="add" :props="props"
                    @click="() => $parent.$emit('_add_row', props.row)">
                </div>
            </q-td>
        </q-tr>
    '''
