from notion_client import Client
from notion.client import NotionClient
from big_thing_py.big_thing import *
# from notion_client.errors import NotionError


class NotionWebClient:

    def __init__(self, token_v2: str = '') -> None:
        self._notion: NotionClient = NotionClient(token_v2=token_v2)

    def get_block(self, block_id: str):
        block = self._notion.get_block(block_id)
        return block


class NotionAPIClient:

    def __init__(self, auth: str = '', database_id: str = '') -> None:
        self._notion = Client(auth=auth)
        self._database_id = database_id

    def get_database_info(self):
        try:
            database = self._notion.databases.retrieve(self._database_id)
            return database
        except Exception as e:
            print('Error occurred while getting database information:', e)

    def add_data(self, name, test_info, input, output):
        try:
            new_page = {
                'Test ID': {'title': [{'text': {'content': name}}]},
                '테스트 내용': {'rich_text': [{'text': {'content': test_info}}]},
                'input': {'rich_text': [{'text': {'content': input}}]},
                'output': {'rich_text': [{'text': {'content': output}}]},
            }
            self._notion.pages.create(parent={'database_id': self._database_id}, properties=new_page)
            print('Data added successfully!')
        except Exception as e:
            print('Error occurred while adding data:', e)

    def delete_data(self, page_id):
        try:
            self._notion.pages.delete(page_id=page_id)
            print('Data deleted successfully!')
        except Exception as e:
            print('Error occurred while deleting data:', e)

    def update_database_title(self, new_title):
        try:
            self._notion.databases.update(self._database_id, title=[{'text': {'content': new_title}}])
            print('Database title updated successfully!')
        except Exception as e:
            print('Error occurred while updating database title:', e)

    def update_data(self, title, property_name, new_value):
        try:
            results = self._notion.databases.query(
                **{
                    'database_id': self._database_id,
                    'filter': {
                        'property': 'Test ID',
                        'title': {
                            'equals': title
                        }
                    }
                }
            ).get('results')

            if len(results) == 0:
                print('Data not found!')
                return

            result = results[0]
            result_id = result.get('id')
            new_page = {property_name: {'rich_text': [{'text': {'content': new_value}}]}}
            self._notion.pages.update(page_id=result_id, properties=new_page)
            print('Data updated successfully!')
        except Exception as e:
            print('Error occurred while updating data:', e)


def async_update(notion_api_client: NotionAPIClient):
    MXThread(target=notion_api_client.update_database_title, args=('test_test',)).start()
    MXThread(target=notion_api_client.add_data, args=('test_1', 'test_1에 대한 내용', 'input1', 'output1')).start()
    MXThread(target=notion_api_client.add_data, args=('test_2', 'test_2에 대한 내용', 'input2', 'output2')).start()
    MXThread(target=notion_api_client.add_data, args=('test_3', 'test_3에 대한 내용', 'input3', 'output3')).start()
    MXThread(target=notion_api_client.add_data, args=('test_4', 'test_4에 대한 내용', 'input4', 'output4')).start()
    MXThread(target=notion_api_client.add_data, args=('test_5', 'test_5에 대한 내용', 'input5', 'output5')).start()
    MXThread(target=notion_api_client.add_data, args=('test_6', 'test_6에 대한 내용', 'input6', 'output6')).start()
    MXThread(target=notion_api_client.update_data, args=('test_1', '테스트 내용', 'new test_1에 대한 내용')).start()


def sync_update(notion_api_client: NotionAPIClient):
    notion_api_client.update_database_title('test_test')
    notion_api_client.add_data('test_6', 'test_6에 대한 내용', 'input6', 'output6')
    notion_api_client.add_data('test_5', 'test_5에 대한 내용', 'input5', 'output5')
    notion_api_client.add_data('test_4', 'test_4에 대한 내용', 'input4', 'output4')
    notion_api_client.add_data('test_3', 'test_3에 대한 내용', 'input3', 'output3')
    notion_api_client.add_data('test_2', 'test_2에 대한 내용', 'input2', 'output2')
    notion_api_client.add_data('test_1', 'test_1에 대한 내용', 'input1', 'output1')
    notion_api_client.update_data('test_1', '테스트 내용', 'new test_1에 대한 내용')


if __name__ == '__main__':
    # MXThread(target=notion_client.get_database_info).start()
    # db_info = notion_client.get_database_info()
    # update_database_title('새로운 디비')
    # notion_client.add_data('test_1', 'test에 대한 내용', 'input1', 'output1')
    # notion_client.update_data('test_1', '테스트 내용', 'new test에 대한 내용', )

    # notion_api_client = NotionAPIClient(auth='secret_B1xvka3NeWUld7KKMR8UqfzTjmzYN5Qo0zaWAoh9tiS',
    #                                     database_id='2e6a1f93330e4278b5225178341de706')
    notion_web_client = NotionWebClient(
        token_v2='v02:user_token_or_cookies:N7t3Mj_Vg2pMQbSp8kJn9fgsfHjzIgbRqsaN6tSMxc8RatBYzQXbeCsv8naB2vfEaoz1dUdazdzsR39iPRquMUL75a_aj4hXZ4pI2gcqAarweynioN3kqaI89ZImBV9c_FUv')

    page = notion_web_client.get_block('https://www.notion.so/thsvkd/2023-04-8c7a40b87e6c47db99a4ee6912e14f4b')
    print("The old title is:", page.title)

    page.title = "The title has now changed, and has *live-updated* in the browser!"

    # async_update(notion_api_client)
    # sync_update(notion_api_client)
