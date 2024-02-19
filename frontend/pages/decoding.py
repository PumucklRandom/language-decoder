import asyncio
from nicegui import ui, app, events, Client
from fastapi.responses import Response
from backend.config.const import URLS, DECODE_COLS
from backend.decoder.pdf import PDF
from frontend.pages.ui_custom import SIZE_FACTOR, ui_dialog, table_item
from frontend.pages.page_abc import Page


class Decoding(Page):

    def __init__(self) -> None:
        super().__init__(url = URLS.DECODING)
        self._client = None
        self.ui_table: ui.table = None  # noqa
        self.input_size: int = 100
        self.s_hash: int = 0
        self.d_hash: int = 0

    def _open_upload(self) -> None:
        self._update_words()
        self.update_url_history()
        ui.open(f'{URLS.UPLOAD}')

    def _open_dictionaries(self) -> None:
        self._update_words()
        self.update_url_history()
        ui.open(f'{URLS.DICTIONARIES}')

    def _open_settings(self) -> None:
        self._update_words()
        self.update_url_history()
        ui.open(f'{URLS.SETTINGS}')

    @staticmethod
    def _open_pdf_view() -> None:
        ui.open(f'{URLS.PDF_VIEW}', new_tab = True)

    def _create_dpf(self) -> str:
        title = self.decoder.title if self.decoder.title else 'decoded'
        download_path = f'{URLS.DOWNLOAD}{self.decoder.uuid}.pdf'
        pdf = PDF(**self.pdf_params)
        buffer = pdf.convert2pdf(
            title = self.decoder.title,
            source_words = self.decoder.source_words,
            target_words = self.decoder.target_words
        )

        @app.get(download_path)
        def download():
            return Response(
                content = buffer,
                media_type = 'application/pdf',
                headers = {
                    'Content-Disposition': f'attachment; filename={title}.pdf'
                },
            )

        @app.get(URLS.PDF_VIEW)
        def pdf_view():
            return Response(
                content = buffer,
                media_type = 'application/pdf',
                headers = {
                    'Content-Disposition': f'inline; filename={title}.pdf'
                },
            )

        return download_path

    def _upd_row(self, event: events.GenericEventArguments) -> None:
        for row in self.ui_table.rows:
            if row.get('id') == event.args.get('id'):
                row.update(event.args)

    def _load_table(self) -> None:
        self._set_input_size()
        self._table.refresh()
        self.ui_table.rows.clear()
        for i, (source, target) in enumerate(zip(self.decoder.source_words, self.decoder.target_words)):
            self.ui_table.rows.append({'id': i, 'source': source, 'target': target})
        self.ui_table.update()

    def _update_words(self) -> None:
        source_words = [row.get('source') for row in self.ui_table.rows]
        target_words = [row.get('target') for row in self.ui_table.rows]
        self.decoder.source_words = source_words
        self.decoder.target_words = target_words

    def _save_words(self):
        self._update_words()
        self._set_input_size()
        self._table.refresh()
        self._load_table()

    def _preload_table(self) -> None:
        self._set_input_size()
        self._table.refresh()
        self.ui_table.rows.clear()
        for i, source in enumerate(self.decoder.source_words):
            self.ui_table.rows.append({'id': i, 'source': source, 'target': ''})
        self.ui_table.update()

    def _set_input_size(self) -> None:
        chars = self.utils.lonlen(self.decoder.source_words + self.decoder.target_words)
        chars = 20 if chars > 20 else chars
        self.input_size = chars * SIZE_FACTOR

    def _split_text(self) -> None:
        _hash = hash(self.decoder.source_text)
        if self.s_hash != _hash:
            self.s_hash = _hash
            self.decoder.split_text()

    async def _decode_words(self) -> None:
        _hash = hash(f'{self.decoder.source_text} {self.decoder.source_language} {self.decoder.target_language}')
        if self.decoder.source_text and self.d_hash != _hash:
            self.d_hash = _hash
            # FIXME: strange JavaScript TimeoutError with notification (over ~380 words)
            #   but applications seems to run anyway
            notification = ui.notification(
                message = f'{self.ui_language.DECODING.Messages.decoding} {len(self.decoder.source_words)}',
                position = 'top',
                type = 'ongoing',
                multi_line = True,
                timeout = None,
                spinner = True,
                close_button = False,
            )
            await asyncio.to_thread(self.decoder.decode_words)
            self.decoder.apply_dict()
            notification.dismiss()
        self._load_table()

    def _apply_dict(self):
        self.decoder.apply_dict()
        self._load_table()

    def _dialog(self) -> ui_dialog:
        return ui_dialog(label_list = self.ui_language.DECODING.Dialogs)

    async def _pdf_dialog(self) -> None:
        self._save_words()
        download_path = self._create_dpf()
        with ui.dialog() as dialog:
            with ui.card().classes('items-center'):
                ui.button(icon = 'close', on_click = dialog.close) \
                    .classes('absolute-top-right') \
                    .props('dense round size=12px')
                ui.space()
                ui.label(self.ui_language.DECODING.Dialogs_pdf[0])
                ui.label(self.ui_language.DECODING.Dialogs_pdf[1])
                ui.button(text = 'VIEW PDF', on_click = self._open_pdf_view)
                ui.label(self.ui_language.DECODING.Dialogs_pdf[2])
                ui.button(text = 'DOWNLOAD', on_click = lambda: ui.download(download_path))
                dialog.open()
        # Cleanup download route after client disconnect
        # FIXME: AttributeError after some time. Applications seems to run anyway
        with await self._client.disconnected():
            app.routes[:] = [route for route in app.routes if route.path != download_path]

    def _header(self) -> None:
        with ui.header():
            ui.button(text = 'GO BACK TO UPLOAD', on_click = self._open_upload)
            ui.label('DECODING').classes('absolute-center')
            ui.space()
            ui.button(text = 'DICTIONARIES', on_click = self._open_dictionaries)
            ui.button(icon = 'settings', on_click = self._open_settings)

    async def _center(self) -> None:
        self._split_text()
        with ui.column().classes('w-full items-center'):
            with ui.card().style('min-width:1000px; min-height:562px'):
                self._table()  # noqa
        self._preload_table()
        await self._decode_words()
        with ui.row().classes('absolute-top-right').style('gap:0.0rem'):
            with ui.column().style('gap:0.0rem'):
                ui.space().style('height:5px')
                with ui.button(icon = 'help', on_click = self._dialog().open).props('dense'):
                    if self.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.help).style('width:70px')
            ui.space().style('width:5px')

    @ui.refreshable
    def _table(self) -> None:
        # TODO: custom size/width for each input element pair
        self.ui_table = ui.table(columns = DECODE_COLS, rows = [], row_key = 'id') \
            .props('hide-header grid')
        self.ui_table.add_slot('item', table_item(self.input_size))
        self.ui_table.on('_upd_row', self._upd_row)

    def _footer(self) -> None:
        with ui.footer():
            with ui.button(text = 'IMPORT', on_click = None):
                if self.show_tips: ui.tooltip('Import words')
            with ui.button(icon = 'save', on_click = self._save_words) \
                    .classes('absolute-center'):
                if self.show_tips: ui.tooltip(self.ui_language.DECODING.Tips.save)
            ui.space().style('width: 400px')
            ui.button(text = 'APPLY DICT', on_click = self._apply_dict)
            ui.button(text = 'CREATE PDF', on_click = self._pdf_dialog)
            ui.space()
            with ui.button(text = 'Export', on_click = None):
                if self.show_tips: ui.tooltip('Export words')

    async def page(self, client: Client) -> None:
        self._client = client
        self.__init_ui__()
        await self._center()
        self._header()
        self._footer()
