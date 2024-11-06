# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: ondewo/s2t/speech-to-text.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'ondewo/s2t/speech-to-text.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fondewo/s2t/speech-to-text.proto\x12\nondewo.s2t\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1cgoogle/protobuf/struct.proto\"\xed\x05\n\x17TranscribeRequestConfig\x12\x17\n\x0fs2t_pipeline_id\x18\x01 \x01(\t\x12&\n\x08\x64\x65\x63oding\x18\x02 \x01(\x0e\x32\x14.ondewo.s2t.Decoding\x12\x1d\n\x13language_model_name\x18\x03 \x01(\tH\x00\x12<\n\x0fpost_processing\x18\x04 \x01(\x0b\x32!.ondewo.s2t.PostProcessingOptionsH\x01\x12\x44\n\x13utterance_detection\x18\x05 \x01(\x0b\x32%.ondewo.s2t.UtteranceDetectionOptionsH\x02\x12(\n\x08pyannote\x18\x06 \x01(\x0b\x32\x14.ondewo.s2t.PyannoteH\x03\x12@\n\x0ereturn_options\x18\x08 \x01(\x0b\x32&.ondewo.s2t.TranscriptionReturnOptionsH\x04\x12\x15\n\x08language\x18\t \x01(\tH\x06\x88\x01\x01\x12\x11\n\x04task\x18\n \x01(\tH\x07\x88\x01\x01\x12\x38\n\x12s2t_service_config\x18\x0b \x01(\x0b\x32\x17.google.protobuf.StructH\x08\x88\x01\x01\x12G\n\x19s2t_cloud_provider_config\x18\x0c \x01(\x0b\x32\".ondewo.s2t.S2tCloudProviderConfigH\x05\x42\x1b\n\x19oneof_language_model_nameB\x17\n\x15oneof_post_processingB\x1b\n\x19oneof_utterance_detectionB\x1a\n\x18voice_activity_detectionB\x16\n\x14oneof_return_optionsB!\n\x1foneof_s2t_cloud_provider_configB\x0b\n\t_languageB\x07\n\x05_taskB\x15\n\x13_s2t_service_config\"\x84\x03\n\x16S2tCloudProviderConfig\x12Y\n$s2t_cloud_provider_config_amazon_aws\x18\x01 \x01(\x0b\x32+.ondewo.s2t.S2tCloudProviderConfigAmazonAws\x12V\n\"s2t_cloud_provider_config_deepgram\x18\x02 \x01(\x0b\x32*.ondewo.s2t.S2tCloudProviderConfigDeepgram\x12R\n s2t_cloud_provider_config_google\x18\x03 \x01(\x0b\x32(.ondewo.s2t.S2tCloudProviderConfigGoogle\x12\x63\n)s2t_cloud_provider_config_microsoft_azure\x18\x04 \x01(\x0b\x32\x30.ondewo.s2t.S2tCloudProviderConfigMicrosoftAzure\"\xa8\x01\n\x1fS2tCloudProviderConfigAmazonAws\x12,\n$enable_partial_results_stabilization\x18\x01 \x01(\x08\x12!\n\x19partial_results_stability\x18\x02 \x01(\t\x12\x1b\n\x13language_model_name\x18\x03 \x01(\t\x12\x17\n\x0fvocabulary_name\x18\x04 \x01(\t\"\x84\x01\n\x1eS2tCloudProviderConfigDeepgram\x12\x11\n\tpunctuate\x18\x01 \x01(\x08\x12\x14\n\x0csmart_format\x18\x02 \x01(\x08\x12\x10\n\x08numerals\x18\x03 \x01(\x08\x12\x14\n\x0cmeasurements\x18\x04 \x01(\x08\x12\x11\n\tdictation\x18\x05 \x01(\x08\"\xc2\x01\n\x1cS2tCloudProviderConfigGoogle\x12$\n\x1c\x65nable_automatic_punctuation\x18\x01 \x01(\x08\x12 \n\x18\x65nable_word_time_offsets\x18\x02 \x01(\x08\x12\x1e\n\x16\x65nable_word_confidence\x18\x03 \x01(\x08\x12 \n\x18transcript_normalization\x18\x04 \x01(\x08\x12\x18\n\x10max_alternatives\x18\x05 \x01(\x05\"n\n$S2tCloudProviderConfigMicrosoftAzure\x12\"\n\x1ause_fast_transcription_api\x18\x01 \x01(\x08\x12\"\n\x1ause_detailed_output_format\x18\x02 \x01(\x08\"\xaf\x02\n\x1aTranscriptionReturnOptions\x12\x1e\n\x16return_start_of_speech\x18\x01 \x01(\x08\x12\x14\n\x0creturn_audio\x18\x02 \x01(\x08\x12\x1f\n\x17return_confidence_score\x18\x03 \x01(\x08\x12)\n!return_alternative_transcriptions\x18\x04 \x01(\x08\x12,\n$return_alternative_transcriptions_nr\x18\x05 \x01(\x05\x12 \n\x18return_alternative_words\x18\x06 \x01(\x08\x12#\n\x1breturn_alternative_words_nr\x18\x07 \x01(\x05\x12\x1a\n\x12return_word_timing\x18\x08 \x01(\x08\"u\n\x19UtteranceDetectionOptions\x12\x1e\n\x14transcribe_not_final\x18\x01 \x01(\x08H\x00\x12\x1a\n\x12next_chunk_timeout\x18\x02 \x01(\x02\x42\x1c\n\x1aoneof_transcribe_not_final\"s\n\x15PostProcessingOptions\x12\x1b\n\x13spelling_correction\x18\x01 \x01(\x08\x12\x11\n\tnormalize\x18\x02 \x01(\x08\x12*\n\x06\x63onfig\x18\x03 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessing\"\xa3\x01\n\rTranscription\x12\x15\n\rtranscription\x18\x01 \x01(\t\x12\x18\n\x10\x63onfidence_score\x18\x02 \x01(\x02\x12%\n\x05words\x18\x03 \x03(\x0b\x32\x16.ondewo.s2t.WordDetail\x12:\n\x0c\x61lternatives\x18\x04 \x03(\x0b\x32$.ondewo.s2t.TranscriptionAlternative\"i\n\x18TranscriptionAlternative\x12\x12\n\ntranscript\x18\x01 \x01(\t\x12\x12\n\nconfidence\x18\x02 \x01(\x02\x12%\n\x05words\x18\x03 \x03(\x0b\x32\x16.ondewo.s2t.WordDetail\"\x8c\x01\n\nWordDetail\x12\x12\n\nstart_time\x18\x01 \x01(\x02\x12\x10\n\x08\x65nd_time\x18\x02 \x01(\x02\x12\x0c\n\x04word\x18\x03 \x01(\t\x12\x12\n\nconfidence\x18\x04 \x01(\x02\x12\x36\n\x11word_alternatives\x18\x05 \x03(\x0b\x32\x1b.ondewo.s2t.WordAlternative\"3\n\x0fWordAlternative\x12\x0c\n\x04word\x18\x01 \x01(\t\x12\x12\n\nconfidence\x18\x02 \x01(\x02\"\x8e\x01\n\x17TranscribeStreamRequest\x12\x13\n\x0b\x61udio_chunk\x18\x01 \x01(\x0c\x12\x15\n\rend_of_stream\x18\x02 \x01(\x08\x12\x33\n\x06\x63onfig\x18\x03 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfig\x12\x12\n\nmute_audio\x18\x04 \x01(\x08\"\x83\x02\n\x18TranscribeStreamResponse\x12\x31\n\x0etranscriptions\x18\x01 \x03(\x0b\x32\x19.ondewo.s2t.Transcription\x12\x0c\n\x04time\x18\x02 \x01(\x02\x12\r\n\x05\x66inal\x18\x03 \x01(\x08\x12\x14\n\x0creturn_audio\x18\x04 \x01(\x08\x12\r\n\x05\x61udio\x18\x05 \x01(\x0c\x12\x17\n\x0futterance_start\x18\x06 \x01(\x08\x12\x12\n\naudio_uuid\x18\x07 \x01(\t\x12\x35\n\x06\x63onfig\x18\x08 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfigH\x00\x42\x0e\n\x0coneof_config\"`\n\x15TranscribeFileRequest\x12\x12\n\naudio_file\x18\x01 \x01(\x0c\x12\x33\n\x06\x63onfig\x18\x02 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfig\"m\n\x16TranscribeFileResponse\x12\x31\n\x0etranscriptions\x18\x01 \x03(\x0b\x32\x19.ondewo.s2t.Transcription\x12\x0c\n\x04time\x18\x02 \x01(\x02\x12\x12\n\naudio_uuid\x18\x03 \x01(\t\"\x1b\n\rS2tPipelineId\x12\n\n\x02id\x18\x01 \x01(\t\"o\n\x17ListS2tPipelinesRequest\x12\x11\n\tlanguages\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\x12\x0f\n\x07\x64omains\x18\x03 \x03(\t\x12\x17\n\x0fregistered_only\x18\x04 \x01(\x08\"S\n\x18ListS2tPipelinesResponse\x12\x37\n\x10pipeline_configs\x18\x01 \x03(\x0b\x32\x1d.ondewo.s2t.Speech2TextConfig\"C\n\x17ListS2tLanguagesRequest\x12\x0f\n\x07\x64omains\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\"-\n\x18ListS2tLanguagesResponse\x12\x11\n\tlanguages\x18\x01 \x03(\t\"C\n\x15ListS2tDomainsRequest\x12\x11\n\tlanguages\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\")\n\x16ListS2tDomainsResponse\x12\x0f\n\x07\x64omains\x18\x01 \x03(\t\",\n\x19S2TGetServiceInfoResponse\x12\x0f\n\x07version\x18\x01 \x01(\t\"\xe5\x02\n\x11Speech2TextConfig\x12\n\n\x02id\x18\x01 \x01(\t\x12/\n\x0b\x64\x65scription\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.S2TDescription\x12\x0e\n\x06\x61\x63tive\x18\x03 \x01(\x08\x12+\n\tinference\x18\x04 \x01(\x0b\x32\x18.ondewo.s2t.S2TInference\x12\x35\n\x10streaming_server\x18\x05 \x01(\x0b\x32\x1b.ondewo.s2t.StreamingServer\x12\x44\n\x18voice_activity_detection\x18\x06 \x01(\x0b\x32\".ondewo.s2t.VoiceActivityDetection\x12\x33\n\x0fpost_processing\x18\x07 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessing\x12$\n\x07logging\x18\x08 \x01(\x0b\x32\x13.ondewo.s2t.Logging\"\\\n\x0eS2TDescription\x12\x10\n\x08language\x18\x01 \x01(\t\x12\x16\n\x0epipeline_owner\x18\x02 \x01(\t\x12\x0e\n\x06\x64omain\x18\x03 \x01(\t\x12\x10\n\x08\x63omments\x18\x04 \x01(\t\"\xb1\x01\n\x0cS2TInference\x12\x33\n\x0f\x61\x63oustic_models\x18\x01 \x01(\x0b\x32\x1a.ondewo.s2t.AcousticModels\x12\x33\n\x0flanguage_models\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.LanguageModels\x12\x37\n\x11inference_backend\x18\x03 \x01(\x0e\x32\x1c.ondewo.s2t.InferenceBackend\"\x80\x04\n\x0e\x41\x63ousticModels\x12\x0c\n\x04type\x18\x01 \x01(\t\x12$\n\x07wav2vec\x18\x02 \x01(\x0b\x32\x13.ondewo.s2t.Wav2Vec\x12\x31\n\x0ewav2vec_triton\x18\x03 \x01(\x0b\x32\x19.ondewo.s2t.Wav2VecTriton\x12$\n\x07whisper\x18\x04 \x01(\x0b\x32\x13.ondewo.s2t.Whisper\x12\x31\n\x0ewhisper_triton\x18\x05 \x01(\x0b\x32\x19.ondewo.s2t.WhisperTriton\x12J\n\x1cs2t_cloud_service_amazon_aws\x18\x06 \x01(\x0b\x32$.ondewo.s2t.S2tCloudServiceAmazonAws\x12G\n\x1as2t_cloud_service_deepgram\x18\x07 \x01(\x0b\x32#.ondewo.s2t.S2tCloudServiceDeepgram\x12\x43\n\x18s2t_cloud_service_google\x18\x08 \x01(\x0b\x32!.ondewo.s2t.S2tCloudServiceGoogle\x12T\n!s2t_cloud_service_microsoft_azure\x18\t \x01(\x0b\x32).ondewo.s2t.S2tCloudServiceMicrosoftAzure\"\xb3\x01\n\x18S2tCloudServiceAmazonAws\x12\x10\n\x08language\x18\x01 \x01(\t\x12,\n$enable_partial_results_stabilization\x18\x02 \x01(\x08\x12!\n\x19partial_results_stability\x18\x03 \x01(\t\x12\x1b\n\x13language_model_name\x18\x04 \x01(\t\x12\x17\n\x0fvocabulary_name\x18\x05 \x01(\t\"\xa3\x01\n\x17S2tCloudServiceDeepgram\x12\x12\n\nmodel_name\x18\x01 \x01(\t\x12\x10\n\x08language\x18\x02 \x01(\t\x12\x11\n\tpunctuate\x18\x03 \x01(\x08\x12\x14\n\x0csmart_format\x18\x04 \x01(\x08\x12\x10\n\x08numerals\x18\x05 \x01(\x08\x12\x14\n\x0cmeasurements\x18\x06 \x01(\x08\x12\x11\n\tdictation\x18\x07 \x01(\x08\"\xe1\x01\n\x15S2tCloudServiceGoogle\x12\x12\n\nmodel_name\x18\x01 \x01(\t\x12\x10\n\x08language\x18\x02 \x01(\t\x12$\n\x1c\x65nable_automatic_punctuation\x18\x03 \x01(\x08\x12 \n\x18\x65nable_word_time_offsets\x18\x04 \x01(\x08\x12\x1e\n\x16\x65nable_word_confidence\x18\x05 \x01(\x08\x12 \n\x18transcript_normalization\x18\x06 \x01(\x08\x12\x18\n\x10max_alternatives\x18\x07 \x01(\x05\"y\n\x1dS2tCloudServiceMicrosoftAzure\x12\x10\n\x08language\x18\x01 \x01(\t\x12\"\n\x1ause_fast_transcription_api\x18\x02 \x01(\x08\x12\"\n\x1ause_detailed_output_format\x18\x03 \x01(\x08\"N\n\x07Whisper\x12\x12\n\nmodel_path\x18\x01 \x01(\t\x12\x0f\n\x07use_gpu\x18\x02 \x01(\x08\x12\x10\n\x08language\x18\x03 \x01(\t\x12\x0c\n\x04task\x18\x04 \x01(\t\"\xd6\x01\n\rWhisperTriton\x12\x16\n\x0eprocessor_path\x18\x01 \x01(\t\x12\x19\n\x11triton_model_name\x18\x02 \x01(\t\x12\x1c\n\x14triton_model_version\x18\x03 \x01(\t\x12\x1c\n\x14\x63heck_status_timeout\x18\x04 \x01(\x03\x12\x10\n\x08language\x18\x05 \x01(\t\x12\x0c\n\x04task\x18\x06 \x01(\t\x12\x1a\n\x12triton_server_host\x18\x07 \x01(\t\x12\x1a\n\x12triton_server_port\x18\x08 \x01(\x03\".\n\x07Wav2Vec\x12\x12\n\nmodel_path\x18\x01 \x01(\t\x12\x0f\n\x07use_gpu\x18\x02 \x01(\x08\"\xb6\x01\n\rWav2VecTriton\x12\x16\n\x0eprocessor_path\x18\x01 \x01(\t\x12\x19\n\x11triton_model_name\x18\x02 \x01(\t\x12\x1c\n\x14triton_model_version\x18\x03 \x01(\t\x12\x1c\n\x14\x63heck_status_timeout\x18\x04 \x01(\x03\x12\x1a\n\x12triton_server_host\x18\x05 \x01(\t\x12\x1a\n\x12triton_server_port\x18\x06 \x01(\x03\"%\n\x07PtFiles\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0c\n\x04step\x18\x02 \x01(\t\"\x18\n\x08\x43kptFile\x12\x0c\n\x04path\x18\x01 \x01(\t\"\x88\x01\n\x0eLanguageModels\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x11\n\tbeam_size\x18\x02 \x01(\x03\x12\x12\n\ndefault_lm\x18\x03 \x01(\t\x12 \n\x18\x62\x65\x61m_search_scorer_alpha\x18\x04 \x01(\x02\x12\x1f\n\x17\x62\x65\x61m_search_scorer_beta\x18\x05 \x01(\x02\"\x91\x01\n\x0fStreamingServer\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x03\x12\x14\n\x0coutput_style\x18\x03 \x01(\t\x12L\n\x1cstreaming_speech_recognition\x18\x04 \x01(\x0b\x32&.ondewo.s2t.StreamingSpeechRecognition\"\xa4\x01\n\x1aStreamingSpeechRecognition\x12\x1c\n\x14transcribe_not_final\x18\x01 \x01(\x08\x12\x17\n\x0f\x64\x65\x63oding_method\x18\x02 \x01(\t\x12\x15\n\rsampling_rate\x18\x03 \x01(\x03\x12\x1c\n\x14min_audio_chunk_size\x18\x04 \x01(\x03\x12\x1a\n\x12next_chunk_timeout\x18\x05 \x01(\x02\"g\n\x16VoiceActivityDetection\x12\x0e\n\x06\x61\x63tive\x18\x01 \x01(\t\x12\x15\n\rsampling_rate\x18\x02 \x01(\x03\x12&\n\x08pyannote\x18\x03 \x01(\x0b\x32\x14.ondewo.s2t.Pyannote\"\xa1\x01\n\x08Pyannote\x12\x12\n\nmodel_name\x18\x01 \x01(\t\x12\x16\n\x0emin_audio_size\x18\x02 \x01(\x03\x12\x18\n\x10min_duration_off\x18\x03 \x01(\x02\x12\x17\n\x0fmin_duration_on\x18\x04 \x01(\x02\x12\x1a\n\x12triton_server_host\x18\x05 \x01(\t\x12\x1a\n\x12triton_server_port\x18\x06 \x01(\x03\"W\n\x0ePostProcessing\x12\x10\n\x08pipeline\x18\x01 \x03(\t\x12\x33\n\x0fpost_processors\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessors\"n\n\x0ePostProcessors\x12\'\n\tsym_spell\x18\x01 \x01(\x0b\x32\x14.ondewo.s2t.SymSpell\x12\x33\n\rnormalization\x18\x02 \x01(\x0b\x32\x1c.ondewo.s2t.S2TNormalization\"Z\n\x08SymSpell\x12\x11\n\tdict_path\x18\x01 \x01(\t\x12$\n\x1cmax_dictionary_edit_distance\x18\x02 \x01(\x03\x12\x15\n\rprefix_length\x18\x03 \x01(\x03\"6\n\x10S2TNormalization\x12\x10\n\x08language\x18\x01 \x01(\t\x12\x10\n\x08pipeline\x18\x02 \x03(\t\"%\n\x07Logging\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\"+\n\x1cListS2tLanguageModelsRequest\x12\x0b\n\x03ids\x18\x01 \x03(\t\"C\n\x17LanguageModelPipelineId\x12\x13\n\x0bpipeline_id\x18\x01 \x01(\t\x12\x13\n\x0bmodel_names\x18\x02 \x03(\t\"]\n\x1dListS2tLanguageModelsResponse\x12<\n\x0flm_pipeline_ids\x18\x01 \x03(\x0b\x32#.ondewo.s2t.LanguageModelPipelineId\"=\n\x1e\x43reateUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\"=\n\x1e\x44\x65leteUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\"U\n!AddDataToUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\x12\x13\n\x0bzipped_data\x18\x02 \x01(\x0c\"K\n\x1dTrainUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\x12\r\n\x05order\x18\x02 \x01(\x03*M\n\x08\x44\x65\x63oding\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x00\x12\n\n\x06GREEDY\x10\x01\x12\x17\n\x13\x42\x45\x41M_SEARCH_WITH_LM\x10\x02\x12\x0f\n\x0b\x42\x45\x41M_SEARCH\x10\x03*l\n\x10InferenceBackend\x12\x1d\n\x19INFERENCE_BACKEND_UNKNOWN\x10\x00\x12\x1d\n\x19INFERENCE_BACKEND_PYTORCH\x10\x01\x12\x1a\n\x16INFERENCE_BACKEND_FLAX\x10\x02\x32\xec\n\n\x0bSpeech2Text\x12Y\n\x0eTranscribeFile\x12!.ondewo.s2t.TranscribeFileRequest\x1a\".ondewo.s2t.TranscribeFileResponse\"\x00\x12\x63\n\x10TranscribeStream\x12#.ondewo.s2t.TranscribeStreamRequest\x1a$.ondewo.s2t.TranscribeStreamResponse\"\x00(\x01\x30\x01\x12L\n\x0eGetS2tPipeline\x12\x19.ondewo.s2t.S2tPipelineId\x1a\x1d.ondewo.s2t.Speech2TextConfig\"\x00\x12O\n\x11\x43reateS2tPipeline\x12\x1d.ondewo.s2t.Speech2TextConfig\x1a\x19.ondewo.s2t.S2tPipelineId\"\x00\x12H\n\x11\x44\x65leteS2tPipeline\x12\x19.ondewo.s2t.S2tPipelineId\x1a\x16.google.protobuf.Empty\"\x00\x12L\n\x11UpdateS2tPipeline\x12\x1d.ondewo.s2t.Speech2TextConfig\x1a\x16.google.protobuf.Empty\"\x00\x12_\n\x10ListS2tPipelines\x12#.ondewo.s2t.ListS2tPipelinesRequest\x1a$.ondewo.s2t.ListS2tPipelinesResponse\"\x00\x12_\n\x10ListS2tLanguages\x12#.ondewo.s2t.ListS2tLanguagesRequest\x1a$.ondewo.s2t.ListS2tLanguagesResponse\"\x00\x12Y\n\x0eListS2tDomains\x12!.ondewo.s2t.ListS2tDomainsRequest\x1a\".ondewo.s2t.ListS2tDomainsResponse\"\x00\x12Q\n\x0eGetServiceInfo\x12\x16.google.protobuf.Empty\x1a%.ondewo.s2t.S2TGetServiceInfoResponse\"\x00\x12n\n\x15ListS2tLanguageModels\x12(.ondewo.s2t.ListS2tLanguageModelsRequest\x1a).ondewo.s2t.ListS2tLanguageModelsResponse\"\x00\x12_\n\x17\x43reateUserLanguageModel\x12*.ondewo.s2t.CreateUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x12_\n\x17\x44\x65leteUserLanguageModel\x12*.ondewo.s2t.DeleteUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x12\x65\n\x1a\x41\x64\x64\x44\x61taToUserLanguageModel\x12-.ondewo.s2t.AddDataToUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x12]\n\x16TrainUserLanguageModel\x12).ondewo.s2t.TrainUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ondewo.s2t.speech_to_text_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_DECODING']._serialized_start=5817
  _globals['_DECODING']._serialized_end=5894
  _globals['_INFERENCEBACKEND']._serialized_start=5896
  _globals['_INFERENCEBACKEND']._serialized_end=6004
  _globals['_TRANSCRIBEREQUESTCONFIG']._serialized_start=77
  _globals['_TRANSCRIBEREQUESTCONFIG']._serialized_end=637
  _globals['_TRANSCRIPTIONRETURNOPTIONS']._serialized_start=640
  _globals['_TRANSCRIPTIONRETURNOPTIONS']._serialized_end=943
  _globals['_UTTERANCEDETECTIONOPTIONS']._serialized_start=945
  _globals['_UTTERANCEDETECTIONOPTIONS']._serialized_end=1062
  _globals['_POSTPROCESSINGOPTIONS']._serialized_start=1064
  _globals['_POSTPROCESSINGOPTIONS']._serialized_end=1179
  _globals['_TRANSCRIPTION']._serialized_start=1182
  _globals['_TRANSCRIPTION']._serialized_end=1345
  _globals['_TRANSCRIPTIONALTERNATIVE']._serialized_start=1347
  _globals['_TRANSCRIPTIONALTERNATIVE']._serialized_end=1452
  _globals['_WORDDETAIL']._serialized_start=1455
  _globals['_WORDDETAIL']._serialized_end=1595
  _globals['_WORDALTERNATIVE']._serialized_start=1597
  _globals['_WORDALTERNATIVE']._serialized_end=1648
  _globals['_TRANSCRIBESTREAMREQUEST']._serialized_start=1651
  _globals['_TRANSCRIBESTREAMREQUEST']._serialized_end=1793
  _globals['_TRANSCRIBESTREAMRESPONSE']._serialized_start=1796
  _globals['_TRANSCRIBESTREAMRESPONSE']._serialized_end=2055
  _globals['_TRANSCRIBEFILEREQUEST']._serialized_start=2057
  _globals['_TRANSCRIBEFILEREQUEST']._serialized_end=2153
  _globals['_TRANSCRIBEFILERESPONSE']._serialized_start=2155
  _globals['_TRANSCRIBEFILERESPONSE']._serialized_end=2264
  _globals['_S2TPIPELINEID']._serialized_start=2266
  _globals['_S2TPIPELINEID']._serialized_end=2293
  _globals['_LISTS2TPIPELINESREQUEST']._serialized_start=2295
  _globals['_LISTS2TPIPELINESREQUEST']._serialized_end=2406
  _globals['_LISTS2TPIPELINESRESPONSE']._serialized_start=2408
  _globals['_LISTS2TPIPELINESRESPONSE']._serialized_end=2491
  _globals['_LISTS2TLANGUAGESREQUEST']._serialized_start=2493
  _globals['_LISTS2TLANGUAGESREQUEST']._serialized_end=2560
  _globals['_LISTS2TLANGUAGESRESPONSE']._serialized_start=2562
  _globals['_LISTS2TLANGUAGESRESPONSE']._serialized_end=2607
  _globals['_LISTS2TDOMAINSREQUEST']._serialized_start=2609
  _globals['_LISTS2TDOMAINSREQUEST']._serialized_end=2676
  _globals['_LISTS2TDOMAINSRESPONSE']._serialized_start=2678
  _globals['_LISTS2TDOMAINSRESPONSE']._serialized_end=2719
  _globals['_S2TGETSERVICEINFORESPONSE']._serialized_start=2721
  _globals['_S2TGETSERVICEINFORESPONSE']._serialized_end=2765
  _globals['_SPEECH2TEXTCONFIG']._serialized_start=2768
  _globals['_SPEECH2TEXTCONFIG']._serialized_end=3125
  _globals['_S2TDESCRIPTION']._serialized_start=3127
  _globals['_S2TDESCRIPTION']._serialized_end=3219
  _globals['_S2TINFERENCE']._serialized_start=3222
  _globals['_S2TINFERENCE']._serialized_end=3399
  _globals['_ACOUSTICMODELS']._serialized_start=3402
  _globals['_ACOUSTICMODELS']._serialized_end=3610
  _globals['_WHISPER']._serialized_start=3612
  _globals['_WHISPER']._serialized_end=3690
  _globals['_WHISPERTRITON']._serialized_start=3693
  _globals['_WHISPERTRITON']._serialized_end=3907
  _globals['_WAV2VEC']._serialized_start=3909
  _globals['_WAV2VEC']._serialized_end=3955
  _globals['_WAV2VECTRITON']._serialized_start=3958
  _globals['_WAV2VECTRITON']._serialized_end=4140
  _globals['_PTFILES']._serialized_start=4142
  _globals['_PTFILES']._serialized_end=4179
  _globals['_CKPTFILE']._serialized_start=4181
  _globals['_CKPTFILE']._serialized_end=4205
  _globals['_LANGUAGEMODELS']._serialized_start=4208
  _globals['_LANGUAGEMODELS']._serialized_end=4344
  _globals['_STREAMINGSERVER']._serialized_start=4347
  _globals['_STREAMINGSERVER']._serialized_end=4492
  _globals['_STREAMINGSPEECHRECOGNITION']._serialized_start=4495
  _globals['_STREAMINGSPEECHRECOGNITION']._serialized_end=4659
  _globals['_VOICEACTIVITYDETECTION']._serialized_start=4661
  _globals['_VOICEACTIVITYDETECTION']._serialized_end=4764
  _globals['_PYANNOTE']._serialized_start=4767
  _globals['_PYANNOTE']._serialized_end=4928
  _globals['_POSTPROCESSING']._serialized_start=4930
  _globals['_POSTPROCESSING']._serialized_end=5017
  _globals['_POSTPROCESSORS']._serialized_start=5019
  _globals['_POSTPROCESSORS']._serialized_end=5129
  _globals['_SYMSPELL']._serialized_start=5131
  _globals['_SYMSPELL']._serialized_end=5221
  _globals['_S2TNORMALIZATION']._serialized_start=5223
  _globals['_S2TNORMALIZATION']._serialized_end=5277
  _globals['_LOGGING']._serialized_start=5279
  _globals['_LOGGING']._serialized_end=5316
  _globals['_LISTS2TLANGUAGEMODELSREQUEST']._serialized_start=5318
  _globals['_LISTS2TLANGUAGEMODELSREQUEST']._serialized_end=5361
  _globals['_LANGUAGEMODELPIPELINEID']._serialized_start=5363
  _globals['_LANGUAGEMODELPIPELINEID']._serialized_end=5430
  _globals['_LISTS2TLANGUAGEMODELSRESPONSE']._serialized_start=5432
  _globals['_LISTS2TLANGUAGEMODELSRESPONSE']._serialized_end=5525
  _globals['_CREATEUSERLANGUAGEMODELREQUEST']._serialized_start=5527
  _globals['_CREATEUSERLANGUAGEMODELREQUEST']._serialized_end=5588
  _globals['_DELETEUSERLANGUAGEMODELREQUEST']._serialized_start=5590
  _globals['_DELETEUSERLANGUAGEMODELREQUEST']._serialized_end=5651
  _globals['_ADDDATATOUSERLANGUAGEMODELREQUEST']._serialized_start=5653
  _globals['_ADDDATATOUSERLANGUAGEMODELREQUEST']._serialized_end=5738
  _globals['_TRAINUSERLANGUAGEMODELREQUEST']._serialized_start=5740
  _globals['_TRAINUSERLANGUAGEMODELREQUEST']._serialized_end=5815
  _globals['_SPEECH2TEXT']._serialized_start=6007
  _globals['_SPEECH2TEXT']._serialized_end=7395
# @@protoc_insertion_point(module_scope)
