# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ondewo/s2t/speech-to-text.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fondewo/s2t/speech-to-text.proto\x12\nondewo.s2t\x1a\x1bgoogle/protobuf/empty.proto\"\xb0\x04\n\x17TranscribeRequestConfig\x12\x17\n\x0fs2t_pipeline_id\x18\x01 \x01(\t\x12&\n\x08\x64\x65\x63oding\x18\x02 \x01(\x0e\x32\x14.ondewo.s2t.Decoding\x12\x1d\n\x13language_model_name\x18\x03 \x01(\tH\x00\x12<\n\x0fpost_processing\x18\x04 \x01(\x0b\x32!.ondewo.s2t.PostProcessingOptionsH\x01\x12\x44\n\x13utterance_detection\x18\x05 \x01(\x0b\x32%.ondewo.s2t.UtteranceDetectionOptionsH\x02\x12(\n\x08pyannote\x18\x06 \x01(\x0b\x32\x14.ondewo.s2t.PyannoteH\x03\x12@\n\x0ereturn_options\x18\x08 \x01(\x0b\x32&.ondewo.s2t.TranscriptionReturnOptionsH\x04\x12\x15\n\x08language\x18\t \x01(\tH\x05\x88\x01\x01\x12\x11\n\x04task\x18\n \x01(\tH\x06\x88\x01\x01\x42\x1b\n\x19oneof_language_model_nameB\x17\n\x15oneof_post_processingB\x1b\n\x19oneof_utterance_detectionB\x1a\n\x18voice_activity_detectionB\x16\n\x14oneof_return_optionsB\x0b\n\t_languageB\x07\n\x05_task\"\xaf\x02\n\x1aTranscriptionReturnOptions\x12\x1e\n\x16return_start_of_speech\x18\x01 \x01(\x08\x12\x14\n\x0creturn_audio\x18\x02 \x01(\x08\x12\x1f\n\x17return_confidence_score\x18\x03 \x01(\x08\x12)\n!return_alternative_transcriptions\x18\x04 \x01(\x08\x12,\n$return_alternative_transcriptions_nr\x18\x05 \x01(\x05\x12 \n\x18return_alternative_words\x18\x06 \x01(\x08\x12#\n\x1breturn_alternative_words_nr\x18\x07 \x01(\x05\x12\x1a\n\x12return_word_timing\x18\x08 \x01(\x08\"\xbf\x01\n\x19UtteranceDetectionOptions\x12\x1e\n\x14transcribe_not_final\x18\x01 \x01(\x08H\x00\x12$\n\x1cstart_of_utterance_threshold\x18\x02 \x01(\x02\x12\"\n\x1a\x65nd_of_utterance_threshold\x18\x03 \x01(\x02\x12\x1a\n\x12next_chunk_timeout\x18\x04 \x01(\x02\x42\x1c\n\x1aoneof_transcribe_not_final\"s\n\x15PostProcessingOptions\x12\x1b\n\x13spelling_correction\x18\x01 \x01(\x08\x12\x11\n\tnormalize\x18\x02 \x01(\x08\x12*\n\x06\x63onfig\x18\x03 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessing\"\xa3\x01\n\rTranscription\x12\x15\n\rtranscription\x18\x01 \x01(\t\x12\x18\n\x10\x63onfidence_score\x18\x02 \x01(\x02\x12%\n\x05words\x18\x03 \x03(\x0b\x32\x16.ondewo.s2t.WordDetail\x12:\n\x0c\x61lternatives\x18\x04 \x03(\x0b\x32$.ondewo.s2t.TranscriptionAlternative\"i\n\x18TranscriptionAlternative\x12\x12\n\ntranscript\x18\x01 \x01(\t\x12\x12\n\nconfidence\x18\x02 \x01(\x02\x12%\n\x05words\x18\x03 \x03(\x0b\x32\x16.ondewo.s2t.WordDetail\"\x8c\x01\n\nWordDetail\x12\x12\n\nstart_time\x18\x01 \x01(\x02\x12\x10\n\x08\x65nd_time\x18\x02 \x01(\x02\x12\x0c\n\x04word\x18\x03 \x01(\t\x12\x12\n\nconfidence\x18\x04 \x01(\x02\x12\x36\n\x11word_alternatives\x18\x05 \x03(\x0b\x32\x1b.ondewo.s2t.WordAlternative\"3\n\x0fWordAlternative\x12\x0c\n\x04word\x18\x01 \x01(\t\x12\x12\n\nconfidence\x18\x02 \x01(\x02\"\x8e\x01\n\x17TranscribeStreamRequest\x12\x13\n\x0b\x61udio_chunk\x18\x01 \x01(\x0c\x12\x15\n\rend_of_stream\x18\x02 \x01(\x08\x12\x33\n\x06\x63onfig\x18\x03 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfig\x12\x12\n\nmute_audio\x18\x04 \x01(\x08\"\x83\x02\n\x18TranscribeStreamResponse\x12\x31\n\x0etranscriptions\x18\x01 \x03(\x0b\x32\x19.ondewo.s2t.Transcription\x12\x0c\n\x04time\x18\x02 \x01(\x02\x12\r\n\x05\x66inal\x18\x03 \x01(\x08\x12\x14\n\x0creturn_audio\x18\x04 \x01(\x08\x12\r\n\x05\x61udio\x18\x05 \x01(\x0c\x12\x17\n\x0futterance_start\x18\x06 \x01(\x08\x12\x12\n\naudio_uuid\x18\x07 \x01(\t\x12\x35\n\x06\x63onfig\x18\x08 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfigH\x00\x42\x0e\n\x0coneof_config\"`\n\x15TranscribeFileRequest\x12\x12\n\naudio_file\x18\x01 \x01(\x0c\x12\x33\n\x06\x63onfig\x18\x02 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfig\"m\n\x16TranscribeFileResponse\x12\x31\n\x0etranscriptions\x18\x01 \x03(\x0b\x32\x19.ondewo.s2t.Transcription\x12\x0c\n\x04time\x18\x02 \x01(\x02\x12\x12\n\naudio_uuid\x18\x03 \x01(\t\"\x1b\n\rS2tPipelineId\x12\n\n\x02id\x18\x01 \x01(\t\"o\n\x17ListS2tPipelinesRequest\x12\x11\n\tlanguages\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\x12\x0f\n\x07\x64omains\x18\x03 \x03(\t\x12\x17\n\x0fregistered_only\x18\x04 \x01(\x08\"S\n\x18ListS2tPipelinesResponse\x12\x37\n\x10pipeline_configs\x18\x01 \x03(\x0b\x32\x1d.ondewo.s2t.Speech2TextConfig\"C\n\x17ListS2tLanguagesRequest\x12\x0f\n\x07\x64omains\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\"-\n\x18ListS2tLanguagesResponse\x12\x11\n\tlanguages\x18\x01 \x03(\t\"C\n\x15ListS2tDomainsRequest\x12\x11\n\tlanguages\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\")\n\x16ListS2tDomainsResponse\x12\x0f\n\x07\x64omains\x18\x01 \x03(\t\",\n\x19S2TGetServiceInfoResponse\x12\x0f\n\x07version\x18\x01 \x01(\t\"\xe5\x02\n\x11Speech2TextConfig\x12\n\n\x02id\x18\x01 \x01(\t\x12/\n\x0b\x64\x65scription\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.S2TDescription\x12\x0e\n\x06\x61\x63tive\x18\x03 \x01(\x08\x12+\n\tinference\x18\x04 \x01(\x0b\x32\x18.ondewo.s2t.S2TInference\x12\x35\n\x10streaming_server\x18\x05 \x01(\x0b\x32\x1b.ondewo.s2t.StreamingServer\x12\x44\n\x18voice_activity_detection\x18\x06 \x01(\x0b\x32\".ondewo.s2t.VoiceActivityDetection\x12\x33\n\x0fpost_processing\x18\x07 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessing\x12$\n\x07logging\x18\x08 \x01(\x0b\x32\x13.ondewo.s2t.Logging\"\\\n\x0eS2TDescription\x12\x10\n\x08language\x18\x01 \x01(\t\x12\x16\n\x0epipeline_owner\x18\x02 \x01(\t\x12\x0e\n\x06\x64omain\x18\x03 \x01(\t\x12\x10\n\x08\x63omments\x18\x04 \x01(\t\"\xb1\x01\n\x0cS2TInference\x12\x33\n\x0f\x61\x63oustic_models\x18\x01 \x01(\x0b\x32\x1a.ondewo.s2t.AcousticModels\x12\x33\n\x0flanguage_models\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.LanguageModels\x12\x37\n\x11inference_backend\x18\x03 \x01(\x0e\x32\x1c.ondewo.s2t.InferenceBackend\"\xd0\x01\n\x0e\x41\x63ousticModels\x12\x0c\n\x04type\x18\x01 \x01(\t\x12$\n\x07wav2vec\x18\x02 \x01(\x0b\x32\x13.ondewo.s2t.Wav2Vec\x12\x31\n\x0ewav2vec_triton\x18\x03 \x01(\x0b\x32\x19.ondewo.s2t.Wav2VecTriton\x12$\n\x07whisper\x18\x04 \x01(\x0b\x32\x13.ondewo.s2t.Whisper\x12\x31\n\x0ewhisper_triton\x18\x05 \x01(\x0b\x32\x19.ondewo.s2t.WhisperTriton\"n\n\x07Whisper\x12\x12\n\nmodel_path\x18\x01 \x01(\t\x12\x0f\n\x07use_gpu\x18\x02 \x01(\x08\x12\x15\n\x08language\x18\x03 \x01(\tH\x00\x88\x01\x01\x12\x11\n\x04task\x18\x04 \x01(\tH\x01\x88\x01\x01\x42\x0b\n\t_languageB\x07\n\x05_task\"\xbe\x01\n\rWhisperTriton\x12\x16\n\x0eprocessor_path\x18\x01 \x01(\t\x12\x19\n\x11triton_model_name\x18\x02 \x01(\t\x12\x1c\n\x14triton_model_version\x18\x03 \x01(\t\x12\x1c\n\x14\x63heck_status_timeout\x18\x04 \x01(\x03\x12\x15\n\x08language\x18\x05 \x01(\tH\x00\x88\x01\x01\x12\x11\n\x04task\x18\x06 \x01(\tH\x01\x88\x01\x01\x42\x0b\n\t_languageB\x07\n\x05_task\".\n\x07Wav2Vec\x12\x12\n\nmodel_path\x18\x01 \x01(\t\x12\x0f\n\x07use_gpu\x18\x02 \x01(\x08\"~\n\rWav2VecTriton\x12\x16\n\x0eprocessor_path\x18\x01 \x01(\t\x12\x19\n\x11triton_model_name\x18\x02 \x01(\t\x12\x1c\n\x14triton_model_version\x18\x03 \x01(\t\x12\x1c\n\x14\x63heck_status_timeout\x18\x04 \x01(\x03\"%\n\x07PtFiles\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0c\n\x04step\x18\x02 \x01(\t\"\x18\n\x08\x43kptFile\x12\x0c\n\x04path\x18\x01 \x01(\t\"\x88\x01\n\x0eLanguageModels\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x11\n\tbeam_size\x18\x02 \x01(\x03\x12\x12\n\ndefault_lm\x18\x03 \x01(\t\x12 \n\x18\x62\x65\x61m_search_scorer_alpha\x18\x04 \x01(\x02\x12\x1f\n\x17\x62\x65\x61m_search_scorer_beta\x18\x05 \x01(\x02\"\x91\x01\n\x0fStreamingServer\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x03\x12\x14\n\x0coutput_style\x18\x03 \x01(\t\x12L\n\x1cstreaming_speech_recognition\x18\x04 \x01(\x0b\x32&.ondewo.s2t.StreamingSpeechRecognition\"\xee\x01\n\x1aStreamingSpeechRecognition\x12\x1c\n\x14transcribe_not_final\x18\x01 \x01(\x08\x12\x17\n\x0f\x64\x65\x63oding_method\x18\x02 \x01(\t\x12\x15\n\rsampling_rate\x18\x03 \x01(\x03\x12\x1c\n\x14min_audio_chunk_size\x18\x04 \x01(\x03\x12$\n\x1cstart_of_utterance_threshold\x18\x05 \x01(\x02\x12\"\n\x1a\x65nd_of_utterance_threshold\x18\x06 \x01(\x02\x12\x1a\n\x12next_chunk_timeout\x18\x07 \x01(\x02\"g\n\x16VoiceActivityDetection\x12\x0e\n\x06\x61\x63tive\x18\x01 \x01(\t\x12\x15\n\rsampling_rate\x18\x02 \x01(\x03\x12&\n\x08pyannote\x18\x03 \x01(\x0b\x32\x14.ondewo.s2t.Pyannote\"i\n\x08Pyannote\x12\x12\n\nmodel_name\x18\x01 \x01(\t\x12\x16\n\x0emin_audio_size\x18\x02 \x01(\x03\x12\x18\n\x10min_duration_off\x18\x03 \x01(\x02\x12\x17\n\x0fmin_duration_on\x18\x04 \x01(\x02\"W\n\x0ePostProcessing\x12\x10\n\x08pipeline\x18\x01 \x03(\t\x12\x33\n\x0fpost_processors\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessors\"n\n\x0ePostProcessors\x12\'\n\tsym_spell\x18\x01 \x01(\x0b\x32\x14.ondewo.s2t.SymSpell\x12\x33\n\rnormalization\x18\x02 \x01(\x0b\x32\x1c.ondewo.s2t.S2TNormalization\"Z\n\x08SymSpell\x12\x11\n\tdict_path\x18\x01 \x01(\t\x12$\n\x1cmax_dictionary_edit_distance\x18\x02 \x01(\x03\x12\x15\n\rprefix_length\x18\x03 \x01(\x03\"$\n\x10S2TNormalization\x12\x10\n\x08language\x18\x01 \x01(\t\"%\n\x07Logging\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\"+\n\x1cListS2tLanguageModelsRequest\x12\x0b\n\x03ids\x18\x01 \x03(\t\"C\n\x17LanguageModelPipelineId\x12\x13\n\x0bpipeline_id\x18\x01 \x01(\t\x12\x13\n\x0bmodel_names\x18\x02 \x03(\t\"]\n\x1dListS2tLanguageModelsResponse\x12<\n\x0flm_pipeline_ids\x18\x01 \x03(\x0b\x32#.ondewo.s2t.LanguageModelPipelineId\"=\n\x1e\x43reateUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\"=\n\x1e\x44\x65leteUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\"U\n!AddDataToUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\x12\x13\n\x0bzipped_data\x18\x02 \x01(\x0c\"K\n\x1dTrainUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\x12\r\n\x05order\x18\x02 \x01(\x03*M\n\x08\x44\x65\x63oding\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x00\x12\n\n\x06GREEDY\x10\x01\x12\x17\n\x13\x42\x45\x41M_SEARCH_WITH_LM\x10\x02\x12\x0f\n\x0b\x42\x45\x41M_SEARCH\x10\x03*l\n\x10InferenceBackend\x12\x1d\n\x19INFERENCE_BACKEND_UNKNOWN\x10\x00\x12\x1d\n\x19INFERENCE_BACKEND_PYTORCH\x10\x01\x12\x1a\n\x16INFERENCE_BACKEND_FLAX\x10\x02\x32\xec\n\n\x0bSpeech2Text\x12Y\n\x0eTranscribeFile\x12!.ondewo.s2t.TranscribeFileRequest\x1a\".ondewo.s2t.TranscribeFileResponse\"\x00\x12\x63\n\x10TranscribeStream\x12#.ondewo.s2t.TranscribeStreamRequest\x1a$.ondewo.s2t.TranscribeStreamResponse\"\x00(\x01\x30\x01\x12L\n\x0eGetS2tPipeline\x12\x19.ondewo.s2t.S2tPipelineId\x1a\x1d.ondewo.s2t.Speech2TextConfig\"\x00\x12O\n\x11\x43reateS2tPipeline\x12\x1d.ondewo.s2t.Speech2TextConfig\x1a\x19.ondewo.s2t.S2tPipelineId\"\x00\x12H\n\x11\x44\x65leteS2tPipeline\x12\x19.ondewo.s2t.S2tPipelineId\x1a\x16.google.protobuf.Empty\"\x00\x12L\n\x11UpdateS2tPipeline\x12\x1d.ondewo.s2t.Speech2TextConfig\x1a\x16.google.protobuf.Empty\"\x00\x12_\n\x10ListS2tPipelines\x12#.ondewo.s2t.ListS2tPipelinesRequest\x1a$.ondewo.s2t.ListS2tPipelinesResponse\"\x00\x12_\n\x10ListS2tLanguages\x12#.ondewo.s2t.ListS2tLanguagesRequest\x1a$.ondewo.s2t.ListS2tLanguagesResponse\"\x00\x12Y\n\x0eListS2tDomains\x12!.ondewo.s2t.ListS2tDomainsRequest\x1a\".ondewo.s2t.ListS2tDomainsResponse\"\x00\x12Q\n\x0eGetServiceInfo\x12\x16.google.protobuf.Empty\x1a%.ondewo.s2t.S2TGetServiceInfoResponse\"\x00\x12n\n\x15ListS2tLanguageModels\x12(.ondewo.s2t.ListS2tLanguageModelsRequest\x1a).ondewo.s2t.ListS2tLanguageModelsResponse\"\x00\x12_\n\x17\x43reateUserLanguageModel\x12*.ondewo.s2t.CreateUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x12_\n\x17\x44\x65leteUserLanguageModel\x12*.ondewo.s2t.DeleteUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x12\x65\n\x1a\x41\x64\x64\x44\x61taToUserLanguageModel\x12-.ondewo.s2t.AddDataToUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x12]\n\x16TrainUserLanguageModel\x12).ondewo.s2t.TrainUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ondewo.s2t.speech_to_text_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_DECODING']._serialized_start=5842
  _globals['_DECODING']._serialized_end=5919
  _globals['_INFERENCEBACKEND']._serialized_start=5921
  _globals['_INFERENCEBACKEND']._serialized_end=6029
  _globals['_TRANSCRIBEREQUESTCONFIG']._serialized_start=77
  _globals['_TRANSCRIBEREQUESTCONFIG']._serialized_end=637
  _globals['_TRANSCRIPTIONRETURNOPTIONS']._serialized_start=640
  _globals['_TRANSCRIPTIONRETURNOPTIONS']._serialized_end=943
  _globals['_UTTERANCEDETECTIONOPTIONS']._serialized_start=946
  _globals['_UTTERANCEDETECTIONOPTIONS']._serialized_end=1137
  _globals['_POSTPROCESSINGOPTIONS']._serialized_start=1139
  _globals['_POSTPROCESSINGOPTIONS']._serialized_end=1254
  _globals['_TRANSCRIPTION']._serialized_start=1257
  _globals['_TRANSCRIPTION']._serialized_end=1420
  _globals['_TRANSCRIPTIONALTERNATIVE']._serialized_start=1422
  _globals['_TRANSCRIPTIONALTERNATIVE']._serialized_end=1527
  _globals['_WORDDETAIL']._serialized_start=1530
  _globals['_WORDDETAIL']._serialized_end=1670
  _globals['_WORDALTERNATIVE']._serialized_start=1672
  _globals['_WORDALTERNATIVE']._serialized_end=1723
  _globals['_TRANSCRIBESTREAMREQUEST']._serialized_start=1726
  _globals['_TRANSCRIBESTREAMREQUEST']._serialized_end=1868
  _globals['_TRANSCRIBESTREAMRESPONSE']._serialized_start=1871
  _globals['_TRANSCRIBESTREAMRESPONSE']._serialized_end=2130
  _globals['_TRANSCRIBEFILEREQUEST']._serialized_start=2132
  _globals['_TRANSCRIBEFILEREQUEST']._serialized_end=2228
  _globals['_TRANSCRIBEFILERESPONSE']._serialized_start=2230
  _globals['_TRANSCRIBEFILERESPONSE']._serialized_end=2339
  _globals['_S2TPIPELINEID']._serialized_start=2341
  _globals['_S2TPIPELINEID']._serialized_end=2368
  _globals['_LISTS2TPIPELINESREQUEST']._serialized_start=2370
  _globals['_LISTS2TPIPELINESREQUEST']._serialized_end=2481
  _globals['_LISTS2TPIPELINESRESPONSE']._serialized_start=2483
  _globals['_LISTS2TPIPELINESRESPONSE']._serialized_end=2566
  _globals['_LISTS2TLANGUAGESREQUEST']._serialized_start=2568
  _globals['_LISTS2TLANGUAGESREQUEST']._serialized_end=2635
  _globals['_LISTS2TLANGUAGESRESPONSE']._serialized_start=2637
  _globals['_LISTS2TLANGUAGESRESPONSE']._serialized_end=2682
  _globals['_LISTS2TDOMAINSREQUEST']._serialized_start=2684
  _globals['_LISTS2TDOMAINSREQUEST']._serialized_end=2751
  _globals['_LISTS2TDOMAINSRESPONSE']._serialized_start=2753
  _globals['_LISTS2TDOMAINSRESPONSE']._serialized_end=2794
  _globals['_S2TGETSERVICEINFORESPONSE']._serialized_start=2796
  _globals['_S2TGETSERVICEINFORESPONSE']._serialized_end=2840
  _globals['_SPEECH2TEXTCONFIG']._serialized_start=2843
  _globals['_SPEECH2TEXTCONFIG']._serialized_end=3200
  _globals['_S2TDESCRIPTION']._serialized_start=3202
  _globals['_S2TDESCRIPTION']._serialized_end=3294
  _globals['_S2TINFERENCE']._serialized_start=3297
  _globals['_S2TINFERENCE']._serialized_end=3474
  _globals['_ACOUSTICMODELS']._serialized_start=3477
  _globals['_ACOUSTICMODELS']._serialized_end=3685
  _globals['_WHISPER']._serialized_start=3687
  _globals['_WHISPER']._serialized_end=3797
  _globals['_WHISPERTRITON']._serialized_start=3800
  _globals['_WHISPERTRITON']._serialized_end=3990
  _globals['_WAV2VEC']._serialized_start=3992
  _globals['_WAV2VEC']._serialized_end=4038
  _globals['_WAV2VECTRITON']._serialized_start=4040
  _globals['_WAV2VECTRITON']._serialized_end=4166
  _globals['_PTFILES']._serialized_start=4168
  _globals['_PTFILES']._serialized_end=4205
  _globals['_CKPTFILE']._serialized_start=4207
  _globals['_CKPTFILE']._serialized_end=4231
  _globals['_LANGUAGEMODELS']._serialized_start=4234
  _globals['_LANGUAGEMODELS']._serialized_end=4370
  _globals['_STREAMINGSERVER']._serialized_start=4373
  _globals['_STREAMINGSERVER']._serialized_end=4518
  _globals['_STREAMINGSPEECHRECOGNITION']._serialized_start=4521
  _globals['_STREAMINGSPEECHRECOGNITION']._serialized_end=4759
  _globals['_VOICEACTIVITYDETECTION']._serialized_start=4761
  _globals['_VOICEACTIVITYDETECTION']._serialized_end=4864
  _globals['_PYANNOTE']._serialized_start=4866
  _globals['_PYANNOTE']._serialized_end=4971
  _globals['_POSTPROCESSING']._serialized_start=4973
  _globals['_POSTPROCESSING']._serialized_end=5060
  _globals['_POSTPROCESSORS']._serialized_start=5062
  _globals['_POSTPROCESSORS']._serialized_end=5172
  _globals['_SYMSPELL']._serialized_start=5174
  _globals['_SYMSPELL']._serialized_end=5264
  _globals['_S2TNORMALIZATION']._serialized_start=5266
  _globals['_S2TNORMALIZATION']._serialized_end=5302
  _globals['_LOGGING']._serialized_start=5304
  _globals['_LOGGING']._serialized_end=5341
  _globals['_LISTS2TLANGUAGEMODELSREQUEST']._serialized_start=5343
  _globals['_LISTS2TLANGUAGEMODELSREQUEST']._serialized_end=5386
  _globals['_LANGUAGEMODELPIPELINEID']._serialized_start=5388
  _globals['_LANGUAGEMODELPIPELINEID']._serialized_end=5455
  _globals['_LISTS2TLANGUAGEMODELSRESPONSE']._serialized_start=5457
  _globals['_LISTS2TLANGUAGEMODELSRESPONSE']._serialized_end=5550
  _globals['_CREATEUSERLANGUAGEMODELREQUEST']._serialized_start=5552
  _globals['_CREATEUSERLANGUAGEMODELREQUEST']._serialized_end=5613
  _globals['_DELETEUSERLANGUAGEMODELREQUEST']._serialized_start=5615
  _globals['_DELETEUSERLANGUAGEMODELREQUEST']._serialized_end=5676
  _globals['_ADDDATATOUSERLANGUAGEMODELREQUEST']._serialized_start=5678
  _globals['_ADDDATATOUSERLANGUAGEMODELREQUEST']._serialized_end=5763
  _globals['_TRAINUSERLANGUAGEMODELREQUEST']._serialized_start=5765
  _globals['_TRAINUSERLANGUAGEMODELREQUEST']._serialized_end=5840
  _globals['_SPEECH2TEXT']._serialized_start=6032
  _globals['_SPEECH2TEXT']._serialized_end=7420
# @@protoc_insertion_point(module_scope)
