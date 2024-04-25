import os

from speechkit import Session
from recognize import recognize
from langchain_community.llms import GigaChat
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from synthesize import play_audio, get_synthesized_audio
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    oauth_token = os.getenv("OAUTH_TOKEN")
    catalog_id = os.getenv("CATALOG_ID")

    # Авторизационные данные для работы с GigaChat API
    authorization_data = os.getenv("AUTHORIZATION_DATA")
    llm = GigaChat(
        credentials=authorization_data,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False,
    )

    # Экземпляр класса `Session` можно получать из разных данных
    session = Session.from_yandex_passport_oauth_token(oauth_token, catalog_id)
    print("Говорите")
    text = recognize(session)
    print("Конец записи")
    print(text)
    prompt = PromptTemplate.from_template(text)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    generated = llm_chain.invoke(input={})
    answer = generated["text"]
    print(answer)
    # get_synthesized_audio(answer) #  сохранение в файл
    play_audio(answer, session)
