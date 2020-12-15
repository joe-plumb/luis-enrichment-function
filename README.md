# luis-enrichment-example

A Python Azure Function to process and enrich output from [Azure Batch Speech-to-text](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/batch-transcription) with a Language Understanding (LUIS) model.

![overview screenshot of function capability. 1. Transcribe audio at scale with Azure Batch Transcription. Write the output into the Azure blob container that triggers your Azure Function. 2. Azure Function BlobEvent Trigger fires on new transcription(s) landing in the blob container. Function parses and iterates over utterances in the transcription and embeds LUIS response in the file. 3. LUIS Cognitive Service identifies known intents and entities in transcribed content. 4. Enriched files stored in new Azure blob container for downstream analytics. Consume data directly in a visualisation tool, or apply further processing and transformations to include in broader analytics ecosystems](/img/overview.png)

Use this function to parse transcribed text to identify *entities* and *intents* from audio.

## Pre-requisites
This repo assumes the user has already set up:
- [Azure Functions service](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python)
- [LUIS Cognitive Service and model](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/get-started-portal-build-app)
- [Batch Transcription Cognitive Service](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/batch-transcription)

## Setup
1. Clone this repo into your development environment
1. Install the required python libraries in your environment by running `make install`
1. Update the input binding in `BatchTranscriptionLuisEnrichment/function.json` to reference the folder name in your blob storage account where your Batch Transcriptions are written to.
1. Update the `local.settings.json` with the LUIS secrets and Storage account connection string
1. Test the function is working by [running the function locally](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-local) and uploading an example transcription using Azure Storage Explorer.
1. Check your storage account for the enriched document in the `transcriptions-enriched` folder. You can now [publish the function to your Function App](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python#publish-the-project-to-azure).

## Known Limitations
- The Azure Functions blob storage trigger does not scale to high-throughput scenarios, as [acknowledged in the documentation](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger?tabs=csharp#event-grid-trigger). For scenarios with higher than 100 blob updates per second, Event Grid trigger should be used.
- LUIS currently has a 500 character limit per REST call. Transcribed utterances that are longer than this are currently truncated in the function.