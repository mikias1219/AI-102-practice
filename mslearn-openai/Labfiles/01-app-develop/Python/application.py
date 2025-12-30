import os
import asyncio
from dotenv import load_dotenv

# Add Azure OpenAI package
from openai import AsyncAzureOpenAI

async def main(): 
        
    try: 
    
        # Get configuration settings 
        # Load from shared .env file
        import pathlib
        script_dir = pathlib.Path(__file__).parent
        shared_env = script_dir.parent.parent.parent / 'mslearn-ai-services' / 'Labfiles' / '01-use-azure-ai-services' / 'Python' / '.env'
        
        if shared_env.exists():
            load_dotenv(dotenv_path=shared_env)
        else:
            load_dotenv()
            
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        
        # Configure the Azure OpenAI client
        client = AsyncAzureOpenAI(
            azure_endpoint=azure_oai_endpoint,
            api_key=azure_oai_key,
            api_version="2024-02-15-preview"
        )
        
        # Initialize messages array
        print("\nAdding grounding context from grounding.txt")
        grounding_text = open(file="grounding.txt", encoding="utf8").read().strip()
        messages_array = [{"role": "user", "content": grounding_text}]

        while True:
            # Pause the app to allow the user to enter the system prompt
            print("------------------\nPausing the app to allow you to change the system prompt.\nPress enter to continue...")
            input()

            # Read in system message and prompt for user message
            system_text = open(file="system.txt", encoding="utf8").read().strip()
            user_text = input("Enter user message, or 'quit' to exit: ")
            if user_text.lower() == 'quit' or system_text.lower() == 'quit':
                print('Exiting program...')
                break

            # Format and send the request to the model
            messages_array.append({"role": "system", "content": system_text})
            messages_array.append({"role": "user", "content": user_text})
            await call_openai_model(messages=messages_array, 
                                    model=azure_oai_deployment, 
                                    client=client
                                    )

    except Exception as ex:
        print(ex)

# Define the function that will get the response from Azure OpenAI endpoint
async def call_openai_model(messages, model, client):
    # Get response from Azure OpenAI
    print("\nSending request to Azure OpenAI model...\n")

    # Call the Azure OpenAI model
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=800
    )

    print("Response:\n" + response.choices[0].message.content + "\n")
    messages.append({"role": "assistant", "content": response.choices[0].message.content})

if __name__ == '__main__': 
    asyncio.run(main())
