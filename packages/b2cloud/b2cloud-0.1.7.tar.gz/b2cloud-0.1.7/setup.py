# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['b2cloud']

package_data = \
{'': ['*']}

install_requires = \
['PyMuPDF>=1.21.1,<2.0.0', 'lxml>=4.9.2,<5.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'b2cloud',
    'version': '0.1.7',
    'description': 'ヤマト運輸株式会社が提供する送り状発行システムB2クラウドをpythonで利用するパッケージ',
    'long_description': '# b2cloud\n\nヤマト運輸株式会社の『送り状発行システムB2クラウド』を操作して伝票を印刷するためのモジュールです。\n利用にあたっては、ヤマトビジネスメンバーズのaccount情報が必要となります。\n\n## インストール\n\n```shell\npip install b2cloud\n```\n\n## コード例\n\n### 履歴の取得\n\n```python\nimport b2cloud\nimport b2cloud.utilities\n\nsession = b2cloud.login(\'your customer_code\', \'your customer_password\')\ndm = b2cloud.search_history(session, service_type=\'3\')\n\nfor entry in dm[\'feed\'][\'entry\']:\n    print(entry[\'shipment\'][\'tracking_number\'], entry[\'shipment\'][\'consignee_name\'])\n```\n\n### 新規に伝票を作成し、データに不備がないかチェックする\n\n```python\n# 伝票情報を生成する\nshipment = b2cloud.utilities.create_dm_shipment(\n    shipment_date=\'2022/12/24\',\n    consignee_telephone_display=\'00-0000-0000\',\n    consignee_name=\'テスト\',\n    consignee_zip_code=\'8900053\',\n    consignee_address1=\'鹿児島県\',\n    consignee_address2=\'鹿児島市\',\n    consignee_address3=\'中央町10\',\n    consignee_address4=\'キャンセビル６階\',\n    consignee_department1=\'インターマン株式会社\'\n)\n\n# データに不備がないかチェックする\nres = b2cloud.check_shipment(session, shipment)\nprint(res)\n\ne.g.\n{\'success\': True, \'errors\': []}\n```\n\n### 伝票の新規保存\n\n```python\n# shipmentsをpost_new_checkonlyを通す\nchecked_feed = b2cloud.post_new_checkonly(session, [shipment])\n# 伝票情報をB2クラウドに保存する\nres = b2cloud.post_new(session, checked_feed)\n```\n\n### 保存した伝票をDM形式で印刷し各伝票毎にPDFファイルに保存する\n\n```python\n# 保存済みのDM伝票を取得\ndm_feed = b2cloud.get_new(session, params={\'service_type\':\'3\'})\n# DM伝票形式（１シート8枚）で印刷\ndm_pdf = b2cloud.print_issue(session,\'3\', dm_feed)\n# １伝票毎に分割する\npdfs = b2cloud.utilities.split_pdf_dm(dm_pdf)\nfor i in range(len(pdfs)):\n    with open(f\'dm_{i}.pdf\', \'wb\') as f:\n        f.write(pdfs[i])\n```\n\n### 住所を伝票情報に変換する\n\n住所正規化サービスAddressian([https://addressian.netlify.app/](https://addressian.netlify.app/))のAPI Keyが必要です。\n\n```python\nconsignee_address = b2cloud.utilities.get_address_info(\n                                                session=session,\n                                                addressian_api_key=\'abcdefghijklmnopqrtsuvwxyz1234567890\',\n                                                address=\'鹿児島市中央町10キャンセビル6F\'\n                                            )\nprint(consignee_address)\n\ne.g.\n{\n    "consignee_zip_code": "8900053",\n    "consignee_address1": "鹿児島県",\n    "consignee_address2": "鹿児島市",\n    "consignee_address3": "中央町10",\n    "consignee_address4": "キャンセビル6F"\n}\n```\n\n## pytest\n\nパラメータでログイン情報やaddressian_api_keyを指定します。\n\n※注意\n\nテストを実行するとテスト伝票が発行されます。\nテスト実行後は、B2クラウドWEBサイトにログインして「保存分の発行」や「発行済みデータの検索」からテストデータを削除することをお勧めします。\n\n### pytest コマンド例\n\n```shell\npytest -q tests/test_01.py  --customer_code=0123456789 --customer_password=abcdefghi --addressian_api_key=abcdefghijklmnopqrtsuvwxyz1234567890\n```\n\n### パラメーターの一覧\n\n```python\nparser.addoption("--customer_code",      action="store", default="")\nparser.addoption("--customer_password",  action="store", default="")\nparser.addoption("--customer_cls_cocde", action="store", default="")\nparser.addoption("--login_user_id",      action="store", default="")\nparser.addoption("--addressian_api_key", action="store", default="")\n```\n',
    'author': 'hgs-interman',
    'author_email': 'naofumi.higashikawauchi@interman.co.jp',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.interman.jp/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
