# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ondewo/s2t/speech-to-text.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fondewo/s2t/speech-to-text.proto\x12\nondewo.s2t\x1a\x1bgoogle/protobuf/empty.proto\"\xa1\x04\n\x17TranscribeRequestConfig\x12\x17\n\x0fs2t_pipeline_id\x18\x01 \x01(\t\x12-\n\x0c\x63tc_decoding\x18\x02 \x01(\x0e\x32\x17.ondewo.s2t.CTCDecoding\x12\x1d\n\x13language_model_name\x18\x03 \x01(\tH\x00\x12<\n\x0fpost_processing\x18\x04 \x01(\x0b\x32!.ondewo.s2t.PostProcessingOptionsH\x01\x12\x44\n\x13utterance_detection\x18\x05 \x01(\x0b\x32%.ondewo.s2t.UtteranceDetectionOptionsH\x02\x12(\n\x08pyannote\x18\x06 \x01(\x0b\x32\x14.ondewo.s2t.PyannoteH\x03\x12(\n\x08matchbox\x18\x07 \x01(\x0b\x32\x14.ondewo.s2t.MatchboxH\x03\x12@\n\x0ereturn_options\x18\x08 \x01(\x0b\x32&.ondewo.s2t.TranscriptionReturnOptionsH\x04\x42\x1b\n\x19oneof_language_model_nameB\x17\n\x15oneof_post_processingB\x1b\n\x19oneof_utterance_detectionB\x1a\n\x18voice_activity_detectionB\x16\n\x14oneof_return_options\"\xba\x01\n\x1aTranscriptionReturnOptions\x12\x1e\n\x16return_start_of_speech\x18\x01 \x01(\x08\x12\x14\n\x0creturn_audio\x18\x02 \x01(\x08\x12)\n!return_alternative_transcriptions\x18\x03 \x01(\x08\x12\x1f\n\x17return_confidence_score\x18\x04 \x01(\x08\x12\x1a\n\x12return_word_timing\x18\x08 \x01(\x08\"\xbf\x01\n\x19UtteranceDetectionOptions\x12\x1e\n\x14transcribe_not_final\x18\x01 \x01(\x08H\x00\x12$\n\x1cstart_of_utterance_threshold\x18\x02 \x01(\x02\x12\"\n\x1a\x65nd_of_utterance_threshold\x18\x03 \x01(\x02\x12\x1a\n\x12next_chunk_timeout\x18\x04 \x01(\x02\x42\x1c\n\x1aoneof_transcribe_not_final\"s\n\x15PostProcessingOptions\x12\x1b\n\x13spelling_correction\x18\x01 \x01(\x08\x12\x11\n\tnormalize\x18\x02 \x01(\x08\x12*\n\x06\x63onfig\x18\x03 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessing\"\x8e\x01\n\x17TranscribeStreamRequest\x12\x13\n\x0b\x61udio_chunk\x18\x01 \x01(\x0c\x12\x15\n\rend_of_stream\x18\x02 \x01(\x08\x12\x33\n\x06\x63onfig\x18\x03 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfig\x12\x12\n\nmute_audio\x18\x04 \x01(\x08\"@\n\rTranscription\x12\x15\n\rtranscription\x18\x01 \x01(\t\x12\x18\n\x10\x63onfidence_score\x18\x02 \x01(\x02\"\x83\x02\n\x18TranscribeStreamResponse\x12\x31\n\x0etranscriptions\x18\x01 \x03(\x0b\x32\x19.ondewo.s2t.Transcription\x12\x0c\n\x04time\x18\x02 \x01(\x02\x12\r\n\x05\x66inal\x18\x03 \x01(\x08\x12\x14\n\x0creturn_audio\x18\x04 \x01(\x08\x12\r\n\x05\x61udio\x18\x05 \x01(\x0c\x12\x17\n\x0futterance_start\x18\x06 \x01(\x08\x12\x12\n\naudio_uuid\x18\x07 \x01(\t\x12\x35\n\x06\x63onfig\x18\x08 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfigH\x00\x42\x0e\n\x0coneof_config\"`\n\x15TranscribeFileRequest\x12\x12\n\naudio_file\x18\x01 \x01(\x0c\x12\x33\n\x06\x63onfig\x18\x02 \x01(\x0b\x32#.ondewo.s2t.TranscribeRequestConfig\"\x9a\x01\n\x16TranscribeFileResponse\x12\x31\n\x0etranscriptions\x18\x01 \x03(\x0b\x32\x19.ondewo.s2t.Transcription\x12\x0c\n\x04time\x18\x02 \x01(\x02\x12+\n\x0bword_timing\x18\x03 \x03(\x0b\x32\x16.ondewo.s2t.WordTiming\x12\x12\n\naudio_uuid\x18\x04 \x01(\t\"6\n\nWordTiming\x12\x0c\n\x04word\x18\x01 \x01(\t\x12\r\n\x05\x62\x65gin\x18\x02 \x01(\x05\x12\x0b\n\x03\x65nd\x18\x03 \x01(\x05\"\x1b\n\rS2tPipelineId\x12\n\n\x02id\x18\x01 \x01(\t\"o\n\x17ListS2tPipelinesRequest\x12\x11\n\tlanguages\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\x12\x0f\n\x07\x64omains\x18\x03 \x03(\t\x12\x17\n\x0fregistered_only\x18\x04 \x01(\x08\"S\n\x18ListS2tPipelinesResponse\x12\x37\n\x10pipeline_configs\x18\x01 \x03(\x0b\x32\x1d.ondewo.s2t.Speech2TextConfig\"C\n\x17ListS2tLanguagesRequest\x12\x0f\n\x07\x64omains\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\"-\n\x18ListS2tLanguagesResponse\x12\x11\n\tlanguages\x18\x01 \x03(\t\"C\n\x15ListS2tDomainsRequest\x12\x11\n\tlanguages\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\")\n\x16ListS2tDomainsResponse\x12\x0f\n\x07\x64omains\x18\x01 \x03(\t\",\n\x19S2TGetServiceInfoResponse\x12\x0f\n\x07version\x18\x01 \x01(\t\"\xe5\x02\n\x11Speech2TextConfig\x12\n\n\x02id\x18\x01 \x01(\t\x12/\n\x0b\x64\x65scription\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.S2TDescription\x12\x0e\n\x06\x61\x63tive\x18\x03 \x01(\x08\x12+\n\tinference\x18\x04 \x01(\x0b\x32\x18.ondewo.s2t.S2TInference\x12\x35\n\x10streaming_server\x18\x05 \x01(\x0b\x32\x1b.ondewo.s2t.StreamingServer\x12\x44\n\x18voice_activity_detection\x18\x06 \x01(\x0b\x32\".ondewo.s2t.VoiceActivityDetection\x12\x33\n\x0fpost_processing\x18\x07 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessing\x12$\n\x07logging\x18\x08 \x01(\x0b\x32\x13.ondewo.s2t.Logging\"\\\n\x0eS2TDescription\x12\x10\n\x08language\x18\x01 \x01(\t\x12\x16\n\x0epipeline_owner\x18\x02 \x01(\t\x12\x0e\n\x06\x64omain\x18\x03 \x01(\t\x12\x10\n\x08\x63omments\x18\x04 \x01(\t\"\x7f\n\x0cS2TInference\x12:\n\x13\x63tc_acoustic_models\x18\x01 \x01(\x0b\x32\x1d.ondewo.s2t.CtcAcousticModels\x12\x33\n\x0flanguage_models\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.LanguageModels\"\xdb\x01\n\x11\x43tcAcousticModels\x12\x0c\n\x04type\x18\x01 \x01(\t\x12(\n\tquartznet\x18\x02 \x01(\x0b\x32\x15.ondewo.s2t.Quartznet\x12\x35\n\x10quartznet_triton\x18\x03 \x01(\x0b\x32\x1b.ondewo.s2t.QuartznetTriton\x12$\n\x07wav2vec\x18\x04 \x01(\x0b\x32\x13.ondewo.s2t.Wav2Vec\x12\x31\n\x0ewav2vec_triton\x18\x05 \x01(\x0b\x32\x19.ondewo.s2t.Wav2VecTriton\".\n\x07Wav2Vec\x12\x12\n\nmodel_path\x18\x01 \x01(\t\x12\x0f\n\x07use_gpu\x18\x02 \x01(\x08\"~\n\rWav2VecTriton\x12\x16\n\x0eprocessor_path\x18\x01 \x01(\t\x12\x19\n\x11triton_model_name\x18\x02 \x01(\t\x12\x1c\n\x14triton_model_version\x18\x03 \x01(\t\x12\x1c\n\x14\x63heck_status_timeout\x18\x04 \x01(\x03\"\x94\x01\n\tQuartznet\x12\x13\n\x0b\x63onfig_path\x18\x01 \x01(\t\x12\x11\n\tload_type\x18\x02 \x01(\t\x12%\n\x08pt_files\x18\x03 \x01(\x0b\x32\x13.ondewo.s2t.PtFiles\x12\'\n\tckpt_file\x18\x04 \x01(\x0b\x32\x14.ondewo.s2t.CkptFile\x12\x0f\n\x07use_gpu\x18\x05 \x01(\x08\"%\n\x07PtFiles\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0c\n\x04step\x18\x02 \x01(\t\"\x18\n\x08\x43kptFile\x12\x0c\n\x04path\x18\x01 \x01(\t\"P\n\x0fQuartznetTriton\x12\x13\n\x0b\x63onfig_path\x18\x01 \x01(\t\x12\x12\n\ntriton_url\x18\x02 \x01(\t\x12\x14\n\x0ctriton_model\x18\x03 \x01(\t\"\x88\x01\n\x0eLanguageModels\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x11\n\tbeam_size\x18\x02 \x01(\x03\x12\x12\n\ndefault_lm\x18\x03 \x01(\t\x12 \n\x18\x62\x65\x61m_search_scorer_alpha\x18\x04 \x01(\x02\x12\x1f\n\x17\x62\x65\x61m_search_scorer_beta\x18\x05 \x01(\x02\"\x91\x01\n\x0fStreamingServer\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x03\x12\x14\n\x0coutput_style\x18\x03 \x01(\t\x12L\n\x1cstreaming_speech_recognition\x18\x04 \x01(\x0b\x32&.ondewo.s2t.StreamingSpeechRecognition\"\xf2\x01\n\x1aStreamingSpeechRecognition\x12\x1c\n\x14transcribe_not_final\x18\x01 \x01(\x08\x12\x1b\n\x13\x63tc_decoding_method\x18\x02 \x01(\t\x12\x15\n\rsampling_rate\x18\x03 \x01(\x03\x12\x1c\n\x14min_audio_chunk_size\x18\x04 \x01(\x03\x12$\n\x1cstart_of_utterance_threshold\x18\x05 \x01(\x02\x12\"\n\x1a\x65nd_of_utterance_threshold\x18\x06 \x01(\x02\x12\x1a\n\x12next_chunk_timeout\x18\x07 \x01(\x02\"\x8f\x01\n\x16VoiceActivityDetection\x12\x0e\n\x06\x61\x63tive\x18\x01 \x01(\t\x12\x15\n\rsampling_rate\x18\x02 \x01(\x03\x12&\n\x08pyannote\x18\x03 \x01(\x0b\x32\x14.ondewo.s2t.Pyannote\x12&\n\x08matchbox\x18\x04 \x01(\x0b\x32\x14.ondewo.s2t.Matchbox\"\xb0\x01\n\x08Pyannote\x12\x12\n\nmodel_path\x18\x01 \x01(\t\x12\x16\n\x0emin_audio_size\x18\x02 \x01(\x03\x12\x0e\n\x06offset\x18\x03 \x01(\x02\x12\r\n\x05onset\x18\x04 \x01(\x02\x12\x13\n\tlog_scale\x18\x05 \x01(\x08H\x00\x12\x18\n\x10min_duration_off\x18\x06 \x01(\x02\x12\x17\n\x0fmin_duration_on\x18\x07 \x01(\x02\x42\x11\n\x0foneof_log_scale\"L\n\x08Matchbox\x12\x14\n\x0cmodel_config\x18\x01 \x01(\t\x12\x14\n\x0c\x65ncoder_path\x18\x02 \x01(\t\x12\x14\n\x0c\x64\x65\x63oder_path\x18\x03 \x01(\t\"W\n\x0ePostProcessing\x12\x10\n\x08pipeline\x18\x01 \x03(\t\x12\x33\n\x0fpost_processors\x18\x02 \x01(\x0b\x32\x1a.ondewo.s2t.PostProcessors\"n\n\x0ePostProcessors\x12\'\n\tsym_spell\x18\x01 \x01(\x0b\x32\x14.ondewo.s2t.SymSpell\x12\x33\n\rnormalization\x18\x02 \x01(\x0b\x32\x1c.ondewo.s2t.S2TNormalization\"Z\n\x08SymSpell\x12\x11\n\tdict_path\x18\x01 \x01(\t\x12$\n\x1cmax_dictionary_edit_distance\x18\x02 \x01(\x03\x12\x15\n\rprefix_length\x18\x03 \x01(\x03\"$\n\x10S2TNormalization\x12\x10\n\x08language\x18\x01 \x01(\t\"%\n\x07Logging\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\"+\n\x1cListS2tLanguageModelsRequest\x12\x0b\n\x03ids\x18\x01 \x03(\t\"C\n\x17LanguageModelPipelineId\x12\x13\n\x0bpipeline_id\x18\x01 \x01(\t\x12\x13\n\x0bmodel_names\x18\x02 \x03(\t\"]\n\x1dListS2tLanguageModelsResponse\x12<\n\x0flm_pipeline_ids\x18\x01 \x03(\x0b\x32#.ondewo.s2t.LanguageModelPipelineId\"=\n\x1e\x43reateUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\"=\n\x1e\x44\x65leteUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\"K\n\x1dTrainUserLanguageModelRequest\x12\x1b\n\x13language_model_name\x18\x01 \x01(\t\x12\r\n\x05order\x18\x02 \x01(\x03*?\n\x0b\x43TCDecoding\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x00\x12\n\n\x06GREEDY\x10\x01\x12\x17\n\x13\x42\x45\x41M_SEARCH_WITH_LM\x10\x02\x32\x85\n\n\x0bSpeech2Text\x12Y\n\x0eTranscribeFile\x12!.ondewo.s2t.TranscribeFileRequest\x1a\".ondewo.s2t.TranscribeFileResponse\"\x00\x12\x63\n\x10TranscribeStream\x12#.ondewo.s2t.TranscribeStreamRequest\x1a$.ondewo.s2t.TranscribeStreamResponse\"\x00(\x01\x30\x01\x12L\n\x0eGetS2tPipeline\x12\x19.ondewo.s2t.S2tPipelineId\x1a\x1d.ondewo.s2t.Speech2TextConfig\"\x00\x12O\n\x11\x43reateS2tPipeline\x12\x1d.ondewo.s2t.Speech2TextConfig\x1a\x19.ondewo.s2t.S2tPipelineId\"\x00\x12H\n\x11\x44\x65leteS2tPipeline\x12\x19.ondewo.s2t.S2tPipelineId\x1a\x16.google.protobuf.Empty\"\x00\x12L\n\x11UpdateS2tPipeline\x12\x1d.ondewo.s2t.Speech2TextConfig\x1a\x16.google.protobuf.Empty\"\x00\x12_\n\x10ListS2tPipelines\x12#.ondewo.s2t.ListS2tPipelinesRequest\x1a$.ondewo.s2t.ListS2tPipelinesResponse\"\x00\x12_\n\x10ListS2tLanguages\x12#.ondewo.s2t.ListS2tLanguagesRequest\x1a$.ondewo.s2t.ListS2tLanguagesResponse\"\x00\x12Y\n\x0eListS2tDomains\x12!.ondewo.s2t.ListS2tDomainsRequest\x1a\".ondewo.s2t.ListS2tDomainsResponse\"\x00\x12Q\n\x0eGetServiceInfo\x12\x16.google.protobuf.Empty\x1a%.ondewo.s2t.S2TGetServiceInfoResponse\"\x00\x12n\n\x15ListS2tLanguageModels\x12(.ondewo.s2t.ListS2tLanguageModelsRequest\x1a).ondewo.s2t.ListS2tLanguageModelsResponse\"\x00\x12_\n\x17\x43reateUserLanguageModel\x12*.ondewo.s2t.CreateUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x12_\n\x17\x44\x65leteUserLanguageModel\x12*.ondewo.s2t.DeleteUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x12]\n\x16TrainUserLanguageModel\x12).ondewo.s2t.TrainUserLanguageModelRequest\x1a\x16.google.protobuf.Empty\"\x00\x62\x06proto3')

_CTCDECODING = DESCRIPTOR.enum_types_by_name['CTCDecoding']
CTCDecoding = enum_type_wrapper.EnumTypeWrapper(_CTCDECODING)
DEFAULT = 0
GREEDY = 1
BEAM_SEARCH_WITH_LM = 2


_TRANSCRIBEREQUESTCONFIG = DESCRIPTOR.message_types_by_name['TranscribeRequestConfig']
_TRANSCRIPTIONRETURNOPTIONS = DESCRIPTOR.message_types_by_name['TranscriptionReturnOptions']
_UTTERANCEDETECTIONOPTIONS = DESCRIPTOR.message_types_by_name['UtteranceDetectionOptions']
_POSTPROCESSINGOPTIONS = DESCRIPTOR.message_types_by_name['PostProcessingOptions']
_TRANSCRIBESTREAMREQUEST = DESCRIPTOR.message_types_by_name['TranscribeStreamRequest']
_TRANSCRIPTION = DESCRIPTOR.message_types_by_name['Transcription']
_TRANSCRIBESTREAMRESPONSE = DESCRIPTOR.message_types_by_name['TranscribeStreamResponse']
_TRANSCRIBEFILEREQUEST = DESCRIPTOR.message_types_by_name['TranscribeFileRequest']
_TRANSCRIBEFILERESPONSE = DESCRIPTOR.message_types_by_name['TranscribeFileResponse']
_WORDTIMING = DESCRIPTOR.message_types_by_name['WordTiming']
_S2TPIPELINEID = DESCRIPTOR.message_types_by_name['S2tPipelineId']
_LISTS2TPIPELINESREQUEST = DESCRIPTOR.message_types_by_name['ListS2tPipelinesRequest']
_LISTS2TPIPELINESRESPONSE = DESCRIPTOR.message_types_by_name['ListS2tPipelinesResponse']
_LISTS2TLANGUAGESREQUEST = DESCRIPTOR.message_types_by_name['ListS2tLanguagesRequest']
_LISTS2TLANGUAGESRESPONSE = DESCRIPTOR.message_types_by_name['ListS2tLanguagesResponse']
_LISTS2TDOMAINSREQUEST = DESCRIPTOR.message_types_by_name['ListS2tDomainsRequest']
_LISTS2TDOMAINSRESPONSE = DESCRIPTOR.message_types_by_name['ListS2tDomainsResponse']
_S2TGETSERVICEINFORESPONSE = DESCRIPTOR.message_types_by_name['S2TGetServiceInfoResponse']
_SPEECH2TEXTCONFIG = DESCRIPTOR.message_types_by_name['Speech2TextConfig']
_S2TDESCRIPTION = DESCRIPTOR.message_types_by_name['S2TDescription']
_S2TINFERENCE = DESCRIPTOR.message_types_by_name['S2TInference']
_CTCACOUSTICMODELS = DESCRIPTOR.message_types_by_name['CtcAcousticModels']
_WAV2VEC = DESCRIPTOR.message_types_by_name['Wav2Vec']
_WAV2VECTRITON = DESCRIPTOR.message_types_by_name['Wav2VecTriton']
_QUARTZNET = DESCRIPTOR.message_types_by_name['Quartznet']
_PTFILES = DESCRIPTOR.message_types_by_name['PtFiles']
_CKPTFILE = DESCRIPTOR.message_types_by_name['CkptFile']
_QUARTZNETTRITON = DESCRIPTOR.message_types_by_name['QuartznetTriton']
_LANGUAGEMODELS = DESCRIPTOR.message_types_by_name['LanguageModels']
_STREAMINGSERVER = DESCRIPTOR.message_types_by_name['StreamingServer']
_STREAMINGSPEECHRECOGNITION = DESCRIPTOR.message_types_by_name['StreamingSpeechRecognition']
_VOICEACTIVITYDETECTION = DESCRIPTOR.message_types_by_name['VoiceActivityDetection']
_PYANNOTE = DESCRIPTOR.message_types_by_name['Pyannote']
_MATCHBOX = DESCRIPTOR.message_types_by_name['Matchbox']
_POSTPROCESSING = DESCRIPTOR.message_types_by_name['PostProcessing']
_POSTPROCESSORS = DESCRIPTOR.message_types_by_name['PostProcessors']
_SYMSPELL = DESCRIPTOR.message_types_by_name['SymSpell']
_S2TNORMALIZATION = DESCRIPTOR.message_types_by_name['S2TNormalization']
_LOGGING = DESCRIPTOR.message_types_by_name['Logging']
_LISTS2TLANGUAGEMODELSREQUEST = DESCRIPTOR.message_types_by_name['ListS2tLanguageModelsRequest']
_LANGUAGEMODELPIPELINEID = DESCRIPTOR.message_types_by_name['LanguageModelPipelineId']
_LISTS2TLANGUAGEMODELSRESPONSE = DESCRIPTOR.message_types_by_name['ListS2tLanguageModelsResponse']
_CREATEUSERLANGUAGEMODELREQUEST = DESCRIPTOR.message_types_by_name['CreateUserLanguageModelRequest']
_DELETEUSERLANGUAGEMODELREQUEST = DESCRIPTOR.message_types_by_name['DeleteUserLanguageModelRequest']
_TRAINUSERLANGUAGEMODELREQUEST = DESCRIPTOR.message_types_by_name['TrainUserLanguageModelRequest']
TranscribeRequestConfig = _reflection.GeneratedProtocolMessageType('TranscribeRequestConfig', (_message.Message,), {
  'DESCRIPTOR' : _TRANSCRIBEREQUESTCONFIG,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.TranscribeRequestConfig)
  })
_sym_db.RegisterMessage(TranscribeRequestConfig)

TranscriptionReturnOptions = _reflection.GeneratedProtocolMessageType('TranscriptionReturnOptions', (_message.Message,), {
  'DESCRIPTOR' : _TRANSCRIPTIONRETURNOPTIONS,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.TranscriptionReturnOptions)
  })
_sym_db.RegisterMessage(TranscriptionReturnOptions)

UtteranceDetectionOptions = _reflection.GeneratedProtocolMessageType('UtteranceDetectionOptions', (_message.Message,), {
  'DESCRIPTOR' : _UTTERANCEDETECTIONOPTIONS,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.UtteranceDetectionOptions)
  })
_sym_db.RegisterMessage(UtteranceDetectionOptions)

PostProcessingOptions = _reflection.GeneratedProtocolMessageType('PostProcessingOptions', (_message.Message,), {
  'DESCRIPTOR' : _POSTPROCESSINGOPTIONS,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.PostProcessingOptions)
  })
_sym_db.RegisterMessage(PostProcessingOptions)

TranscribeStreamRequest = _reflection.GeneratedProtocolMessageType('TranscribeStreamRequest', (_message.Message,), {
  'DESCRIPTOR' : _TRANSCRIBESTREAMREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.TranscribeStreamRequest)
  })
_sym_db.RegisterMessage(TranscribeStreamRequest)

Transcription = _reflection.GeneratedProtocolMessageType('Transcription', (_message.Message,), {
  'DESCRIPTOR' : _TRANSCRIPTION,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.Transcription)
  })
_sym_db.RegisterMessage(Transcription)

TranscribeStreamResponse = _reflection.GeneratedProtocolMessageType('TranscribeStreamResponse', (_message.Message,), {
  'DESCRIPTOR' : _TRANSCRIBESTREAMRESPONSE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.TranscribeStreamResponse)
  })
_sym_db.RegisterMessage(TranscribeStreamResponse)

TranscribeFileRequest = _reflection.GeneratedProtocolMessageType('TranscribeFileRequest', (_message.Message,), {
  'DESCRIPTOR' : _TRANSCRIBEFILEREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.TranscribeFileRequest)
  })
_sym_db.RegisterMessage(TranscribeFileRequest)

TranscribeFileResponse = _reflection.GeneratedProtocolMessageType('TranscribeFileResponse', (_message.Message,), {
  'DESCRIPTOR' : _TRANSCRIBEFILERESPONSE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.TranscribeFileResponse)
  })
_sym_db.RegisterMessage(TranscribeFileResponse)

WordTiming = _reflection.GeneratedProtocolMessageType('WordTiming', (_message.Message,), {
  'DESCRIPTOR' : _WORDTIMING,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.WordTiming)
  })
_sym_db.RegisterMessage(WordTiming)

S2tPipelineId = _reflection.GeneratedProtocolMessageType('S2tPipelineId', (_message.Message,), {
  'DESCRIPTOR' : _S2TPIPELINEID,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.S2tPipelineId)
  })
_sym_db.RegisterMessage(S2tPipelineId)

ListS2tPipelinesRequest = _reflection.GeneratedProtocolMessageType('ListS2tPipelinesRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2TPIPELINESREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.ListS2tPipelinesRequest)
  })
_sym_db.RegisterMessage(ListS2tPipelinesRequest)

ListS2tPipelinesResponse = _reflection.GeneratedProtocolMessageType('ListS2tPipelinesResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2TPIPELINESRESPONSE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.ListS2tPipelinesResponse)
  })
_sym_db.RegisterMessage(ListS2tPipelinesResponse)

ListS2tLanguagesRequest = _reflection.GeneratedProtocolMessageType('ListS2tLanguagesRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2TLANGUAGESREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.ListS2tLanguagesRequest)
  })
_sym_db.RegisterMessage(ListS2tLanguagesRequest)

ListS2tLanguagesResponse = _reflection.GeneratedProtocolMessageType('ListS2tLanguagesResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2TLANGUAGESRESPONSE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.ListS2tLanguagesResponse)
  })
_sym_db.RegisterMessage(ListS2tLanguagesResponse)

ListS2tDomainsRequest = _reflection.GeneratedProtocolMessageType('ListS2tDomainsRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2TDOMAINSREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.ListS2tDomainsRequest)
  })
_sym_db.RegisterMessage(ListS2tDomainsRequest)

ListS2tDomainsResponse = _reflection.GeneratedProtocolMessageType('ListS2tDomainsResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2TDOMAINSRESPONSE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.ListS2tDomainsResponse)
  })
_sym_db.RegisterMessage(ListS2tDomainsResponse)

S2TGetServiceInfoResponse = _reflection.GeneratedProtocolMessageType('S2TGetServiceInfoResponse', (_message.Message,), {
  'DESCRIPTOR' : _S2TGETSERVICEINFORESPONSE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.S2TGetServiceInfoResponse)
  })
_sym_db.RegisterMessage(S2TGetServiceInfoResponse)

Speech2TextConfig = _reflection.GeneratedProtocolMessageType('Speech2TextConfig', (_message.Message,), {
  'DESCRIPTOR' : _SPEECH2TEXTCONFIG,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.Speech2TextConfig)
  })
_sym_db.RegisterMessage(Speech2TextConfig)

S2TDescription = _reflection.GeneratedProtocolMessageType('S2TDescription', (_message.Message,), {
  'DESCRIPTOR' : _S2TDESCRIPTION,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.S2TDescription)
  })
_sym_db.RegisterMessage(S2TDescription)

S2TInference = _reflection.GeneratedProtocolMessageType('S2TInference', (_message.Message,), {
  'DESCRIPTOR' : _S2TINFERENCE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.S2TInference)
  })
_sym_db.RegisterMessage(S2TInference)

CtcAcousticModels = _reflection.GeneratedProtocolMessageType('CtcAcousticModels', (_message.Message,), {
  'DESCRIPTOR' : _CTCACOUSTICMODELS,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.CtcAcousticModels)
  })
_sym_db.RegisterMessage(CtcAcousticModels)

Wav2Vec = _reflection.GeneratedProtocolMessageType('Wav2Vec', (_message.Message,), {
  'DESCRIPTOR' : _WAV2VEC,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.Wav2Vec)
  })
_sym_db.RegisterMessage(Wav2Vec)

Wav2VecTriton = _reflection.GeneratedProtocolMessageType('Wav2VecTriton', (_message.Message,), {
  'DESCRIPTOR' : _WAV2VECTRITON,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.Wav2VecTriton)
  })
_sym_db.RegisterMessage(Wav2VecTriton)

Quartznet = _reflection.GeneratedProtocolMessageType('Quartznet', (_message.Message,), {
  'DESCRIPTOR' : _QUARTZNET,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.Quartznet)
  })
_sym_db.RegisterMessage(Quartznet)

PtFiles = _reflection.GeneratedProtocolMessageType('PtFiles', (_message.Message,), {
  'DESCRIPTOR' : _PTFILES,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.PtFiles)
  })
_sym_db.RegisterMessage(PtFiles)

CkptFile = _reflection.GeneratedProtocolMessageType('CkptFile', (_message.Message,), {
  'DESCRIPTOR' : _CKPTFILE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.CkptFile)
  })
_sym_db.RegisterMessage(CkptFile)

QuartznetTriton = _reflection.GeneratedProtocolMessageType('QuartznetTriton', (_message.Message,), {
  'DESCRIPTOR' : _QUARTZNETTRITON,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.QuartznetTriton)
  })
_sym_db.RegisterMessage(QuartznetTriton)

LanguageModels = _reflection.GeneratedProtocolMessageType('LanguageModels', (_message.Message,), {
  'DESCRIPTOR' : _LANGUAGEMODELS,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.LanguageModels)
  })
_sym_db.RegisterMessage(LanguageModels)

StreamingServer = _reflection.GeneratedProtocolMessageType('StreamingServer', (_message.Message,), {
  'DESCRIPTOR' : _STREAMINGSERVER,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.StreamingServer)
  })
_sym_db.RegisterMessage(StreamingServer)

StreamingSpeechRecognition = _reflection.GeneratedProtocolMessageType('StreamingSpeechRecognition', (_message.Message,), {
  'DESCRIPTOR' : _STREAMINGSPEECHRECOGNITION,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.StreamingSpeechRecognition)
  })
_sym_db.RegisterMessage(StreamingSpeechRecognition)

VoiceActivityDetection = _reflection.GeneratedProtocolMessageType('VoiceActivityDetection', (_message.Message,), {
  'DESCRIPTOR' : _VOICEACTIVITYDETECTION,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.VoiceActivityDetection)
  })
_sym_db.RegisterMessage(VoiceActivityDetection)

Pyannote = _reflection.GeneratedProtocolMessageType('Pyannote', (_message.Message,), {
  'DESCRIPTOR' : _PYANNOTE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.Pyannote)
  })
_sym_db.RegisterMessage(Pyannote)

Matchbox = _reflection.GeneratedProtocolMessageType('Matchbox', (_message.Message,), {
  'DESCRIPTOR' : _MATCHBOX,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.Matchbox)
  })
_sym_db.RegisterMessage(Matchbox)

PostProcessing = _reflection.GeneratedProtocolMessageType('PostProcessing', (_message.Message,), {
  'DESCRIPTOR' : _POSTPROCESSING,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.PostProcessing)
  })
_sym_db.RegisterMessage(PostProcessing)

PostProcessors = _reflection.GeneratedProtocolMessageType('PostProcessors', (_message.Message,), {
  'DESCRIPTOR' : _POSTPROCESSORS,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.PostProcessors)
  })
_sym_db.RegisterMessage(PostProcessors)

SymSpell = _reflection.GeneratedProtocolMessageType('SymSpell', (_message.Message,), {
  'DESCRIPTOR' : _SYMSPELL,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.SymSpell)
  })
_sym_db.RegisterMessage(SymSpell)

S2TNormalization = _reflection.GeneratedProtocolMessageType('S2TNormalization', (_message.Message,), {
  'DESCRIPTOR' : _S2TNORMALIZATION,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.S2TNormalization)
  })
_sym_db.RegisterMessage(S2TNormalization)

Logging = _reflection.GeneratedProtocolMessageType('Logging', (_message.Message,), {
  'DESCRIPTOR' : _LOGGING,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.Logging)
  })
_sym_db.RegisterMessage(Logging)

ListS2tLanguageModelsRequest = _reflection.GeneratedProtocolMessageType('ListS2tLanguageModelsRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2TLANGUAGEMODELSREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.ListS2tLanguageModelsRequest)
  })
_sym_db.RegisterMessage(ListS2tLanguageModelsRequest)

LanguageModelPipelineId = _reflection.GeneratedProtocolMessageType('LanguageModelPipelineId', (_message.Message,), {
  'DESCRIPTOR' : _LANGUAGEMODELPIPELINEID,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.LanguageModelPipelineId)
  })
_sym_db.RegisterMessage(LanguageModelPipelineId)

ListS2tLanguageModelsResponse = _reflection.GeneratedProtocolMessageType('ListS2tLanguageModelsResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTS2TLANGUAGEMODELSRESPONSE,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.ListS2tLanguageModelsResponse)
  })
_sym_db.RegisterMessage(ListS2tLanguageModelsResponse)

CreateUserLanguageModelRequest = _reflection.GeneratedProtocolMessageType('CreateUserLanguageModelRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEUSERLANGUAGEMODELREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.CreateUserLanguageModelRequest)
  })
_sym_db.RegisterMessage(CreateUserLanguageModelRequest)

DeleteUserLanguageModelRequest = _reflection.GeneratedProtocolMessageType('DeleteUserLanguageModelRequest', (_message.Message,), {
  'DESCRIPTOR' : _DELETEUSERLANGUAGEMODELREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.DeleteUserLanguageModelRequest)
  })
_sym_db.RegisterMessage(DeleteUserLanguageModelRequest)

TrainUserLanguageModelRequest = _reflection.GeneratedProtocolMessageType('TrainUserLanguageModelRequest', (_message.Message,), {
  'DESCRIPTOR' : _TRAINUSERLANGUAGEMODELREQUEST,
  '__module__' : 'ondewo.s2t.speech_to_text_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.s2t.TrainUserLanguageModelRequest)
  })
_sym_db.RegisterMessage(TrainUserLanguageModelRequest)

_SPEECH2TEXT = DESCRIPTOR.services_by_name['Speech2Text']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CTCDECODING._serialized_start=5405
  _CTCDECODING._serialized_end=5468
  _TRANSCRIBEREQUESTCONFIG._serialized_start=77
  _TRANSCRIBEREQUESTCONFIG._serialized_end=622
  _TRANSCRIPTIONRETURNOPTIONS._serialized_start=625
  _TRANSCRIPTIONRETURNOPTIONS._serialized_end=811
  _UTTERANCEDETECTIONOPTIONS._serialized_start=814
  _UTTERANCEDETECTIONOPTIONS._serialized_end=1005
  _POSTPROCESSINGOPTIONS._serialized_start=1007
  _POSTPROCESSINGOPTIONS._serialized_end=1122
  _TRANSCRIBESTREAMREQUEST._serialized_start=1125
  _TRANSCRIBESTREAMREQUEST._serialized_end=1267
  _TRANSCRIPTION._serialized_start=1269
  _TRANSCRIPTION._serialized_end=1333
  _TRANSCRIBESTREAMRESPONSE._serialized_start=1336
  _TRANSCRIBESTREAMRESPONSE._serialized_end=1595
  _TRANSCRIBEFILEREQUEST._serialized_start=1597
  _TRANSCRIBEFILEREQUEST._serialized_end=1693
  _TRANSCRIBEFILERESPONSE._serialized_start=1696
  _TRANSCRIBEFILERESPONSE._serialized_end=1850
  _WORDTIMING._serialized_start=1852
  _WORDTIMING._serialized_end=1906
  _S2TPIPELINEID._serialized_start=1908
  _S2TPIPELINEID._serialized_end=1935
  _LISTS2TPIPELINESREQUEST._serialized_start=1937
  _LISTS2TPIPELINESREQUEST._serialized_end=2048
  _LISTS2TPIPELINESRESPONSE._serialized_start=2050
  _LISTS2TPIPELINESRESPONSE._serialized_end=2133
  _LISTS2TLANGUAGESREQUEST._serialized_start=2135
  _LISTS2TLANGUAGESREQUEST._serialized_end=2202
  _LISTS2TLANGUAGESRESPONSE._serialized_start=2204
  _LISTS2TLANGUAGESRESPONSE._serialized_end=2249
  _LISTS2TDOMAINSREQUEST._serialized_start=2251
  _LISTS2TDOMAINSREQUEST._serialized_end=2318
  _LISTS2TDOMAINSRESPONSE._serialized_start=2320
  _LISTS2TDOMAINSRESPONSE._serialized_end=2361
  _S2TGETSERVICEINFORESPONSE._serialized_start=2363
  _S2TGETSERVICEINFORESPONSE._serialized_end=2407
  _SPEECH2TEXTCONFIG._serialized_start=2410
  _SPEECH2TEXTCONFIG._serialized_end=2767
  _S2TDESCRIPTION._serialized_start=2769
  _S2TDESCRIPTION._serialized_end=2861
  _S2TINFERENCE._serialized_start=2863
  _S2TINFERENCE._serialized_end=2990
  _CTCACOUSTICMODELS._serialized_start=2993
  _CTCACOUSTICMODELS._serialized_end=3212
  _WAV2VEC._serialized_start=3214
  _WAV2VEC._serialized_end=3260
  _WAV2VECTRITON._serialized_start=3262
  _WAV2VECTRITON._serialized_end=3388
  _QUARTZNET._serialized_start=3391
  _QUARTZNET._serialized_end=3539
  _PTFILES._serialized_start=3541
  _PTFILES._serialized_end=3578
  _CKPTFILE._serialized_start=3580
  _CKPTFILE._serialized_end=3604
  _QUARTZNETTRITON._serialized_start=3606
  _QUARTZNETTRITON._serialized_end=3686
  _LANGUAGEMODELS._serialized_start=3689
  _LANGUAGEMODELS._serialized_end=3825
  _STREAMINGSERVER._serialized_start=3828
  _STREAMINGSERVER._serialized_end=3973
  _STREAMINGSPEECHRECOGNITION._serialized_start=3976
  _STREAMINGSPEECHRECOGNITION._serialized_end=4218
  _VOICEACTIVITYDETECTION._serialized_start=4221
  _VOICEACTIVITYDETECTION._serialized_end=4364
  _PYANNOTE._serialized_start=4367
  _PYANNOTE._serialized_end=4543
  _MATCHBOX._serialized_start=4545
  _MATCHBOX._serialized_end=4621
  _POSTPROCESSING._serialized_start=4623
  _POSTPROCESSING._serialized_end=4710
  _POSTPROCESSORS._serialized_start=4712
  _POSTPROCESSORS._serialized_end=4822
  _SYMSPELL._serialized_start=4824
  _SYMSPELL._serialized_end=4914
  _S2TNORMALIZATION._serialized_start=4916
  _S2TNORMALIZATION._serialized_end=4952
  _LOGGING._serialized_start=4954
  _LOGGING._serialized_end=4991
  _LISTS2TLANGUAGEMODELSREQUEST._serialized_start=4993
  _LISTS2TLANGUAGEMODELSREQUEST._serialized_end=5036
  _LANGUAGEMODELPIPELINEID._serialized_start=5038
  _LANGUAGEMODELPIPELINEID._serialized_end=5105
  _LISTS2TLANGUAGEMODELSRESPONSE._serialized_start=5107
  _LISTS2TLANGUAGEMODELSRESPONSE._serialized_end=5200
  _CREATEUSERLANGUAGEMODELREQUEST._serialized_start=5202
  _CREATEUSERLANGUAGEMODELREQUEST._serialized_end=5263
  _DELETEUSERLANGUAGEMODELREQUEST._serialized_start=5265
  _DELETEUSERLANGUAGEMODELREQUEST._serialized_end=5326
  _TRAINUSERLANGUAGEMODELREQUEST._serialized_start=5328
  _TRAINUSERLANGUAGEMODELREQUEST._serialized_end=5403
  _SPEECH2TEXT._serialized_start=5471
  _SPEECH2TEXT._serialized_end=6756
# @@protoc_insertion_point(module_scope)
