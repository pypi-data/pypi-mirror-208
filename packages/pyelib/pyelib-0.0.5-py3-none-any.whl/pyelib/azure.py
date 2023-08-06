import openai


class ChatGPT:
    def __init__(self, api_type, api_base, api_version, api_key, system_content=""):
        """

        :param api_type:  azure
        :param api_base:  https://xxx.openai.azure.com/
        :param api_version:  2023-03-15-preview
        :param api_key:  xxx
        :param system_content:  系统消息
        """
        openai.api_type = api_type
        openai.api_base = api_base
        openai.api_version = api_version
        openai.api_key = api_key
        self.messages = [{"role": "system", "content": system_content}]

    def chat(self, max_tokens: int = 800):
        """

        :param max_tokens:  最大长度
        :return:
        """
        while True:
            message = input("问题：")
            self.messages.append({"role": "user", "content": message})
            response = openai.ChatCompletion.create(
                engine="gpt",
                messages=self.messages,
                temperature=0.5,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
            reply = response.choices[0].message.content
            print(reply)
            self.messages.append({"role": "assistant", "content": reply})
