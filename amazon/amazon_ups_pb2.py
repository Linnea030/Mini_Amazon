# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: amazon_ups.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x61mazon_ups.proto\x12\x17\x65\x64u.duke.ece568.miniups\"9\n\x08UArrived\x12\x0f\n\x07truckid\x18\x01 \x02(\x05\x12\x0c\n\x04whid\x18\x02 \x02(\x05\x12\x0e\n\x06seqnum\x18\x03 \x02(\x03\"/\n\nUDelivered\x12\x11\n\tpackageid\x18\x01 \x02(\x03\x12\x0e\n\x06seqnum\x18\x02 \x02(\x03\"3\n\x06UError\x12\x0c\n\x04\x63ode\x18\x01 \x02(\x05\x12\x0b\n\x03msg\x18\x02 \x01(\t\x12\x0e\n\x06seqnum\x18\x03 \x02(\x03\")\n\nAPickupReq\x12\x0b\n\x03hid\x18\x01 \x02(\x05\x12\x0e\n\x06seqnum\x18\x02 \x02(\x03\"@\n\x05\x41Item\x12\x0e\n\x06itemid\x18\x01 \x02(\x05\x12\x0b\n\x03num\x18\x02 \x02(\x05\x12\x0c\n\x04name\x18\x03 \x02(\t\x12\x0c\n\x04\x64\x65sc\x18\x04 \x02(\t\";\n\x05\x41Load\x12\x0f\n\x07truckid\x18\x01 \x02(\x05\x12\x11\n\tpackageid\x18\x02 \x02(\x03\x12\x0e\n\x06seqnum\x18\x03 \x02(\x03\"\xa9\x01\n\x0e\x41\x43reatePackage\x12\x0b\n\x03hid\x18\x01 \x02(\x05\x12\x11\n\tpackageid\x18\x02 \x02(\x03\x12\x12\n\nlocation_x\x18\x03 \x02(\x05\x12\x12\n\nlocation_y\x18\x04 \x02(\x05\x12\x0e\n\x06seqnum\x18\x05 \x02(\x03\x12\r\n\x05\x65mail\x18\x06 \x02(\t\x12\x30\n\x08itemInfo\x18\x07 \x03(\x0b\x32\x1e.edu.duke.ece568.miniups.AItem\"0\n\rALoadComplete\x12\x0f\n\x07truckid\x18\x01 \x02(\x05\x12\x0e\n\x06seqnum\x18\x02 \x02(\x03\"3\n\x06\x41\x45rror\x12\x0c\n\x04\x63ode\x18\x01 \x02(\x05\x12\x0b\n\x03msg\x18\x02 \x01(\t\x12\x0e\n\x06seqnum\x18\x03 \x02(\x03\"\x8f\x02\n\x08\x41\x43ommand\x12\x34\n\x07pickups\x18\x01 \x03(\x0b\x32#.edu.duke.ece568.miniups.APickupReq\x12.\n\x06toload\x18\x02 \x03(\x0b\x32\x1e.edu.duke.ece568.miniups.ALoad\x12\x34\n\x04\x63omp\x18\x03 \x03(\x0b\x32&.edu.duke.ece568.miniups.ALoadComplete\x12\x37\n\x06\x63reate\x18\x04 \x03(\x0b\x32\'.edu.duke.ece568.miniups.ACreatePackage\x12.\n\x05\x65rror\x18\x05 \x03(\x0b\x32\x1f.edu.duke.ece568.miniups.AError\"\xa9\x01\n\x08UCommand\x12\x33\n\x08uarrived\x18\x01 \x03(\x0b\x32!.edu.duke.ece568.miniups.UArrived\x12\x37\n\nudelivered\x18\x02 \x03(\x0b\x32#.edu.duke.ece568.miniups.UDelivered\x12/\n\x06uerror\x18\x03 \x03(\x0b\x32\x1f.edu.duke.ece568.miniups.UError')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'amazon_ups_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _UARRIVED._serialized_start=45
  _UARRIVED._serialized_end=102
  _UDELIVERED._serialized_start=104
  _UDELIVERED._serialized_end=151
  _UERROR._serialized_start=153
  _UERROR._serialized_end=204
  _APICKUPREQ._serialized_start=206
  _APICKUPREQ._serialized_end=247
  _AITEM._serialized_start=249
  _AITEM._serialized_end=313
  _ALOAD._serialized_start=315
  _ALOAD._serialized_end=374
  _ACREATEPACKAGE._serialized_start=377
  _ACREATEPACKAGE._serialized_end=546
  _ALOADCOMPLETE._serialized_start=548
  _ALOADCOMPLETE._serialized_end=596
  _AERROR._serialized_start=598
  _AERROR._serialized_end=649
  _ACOMMAND._serialized_start=652
  _ACOMMAND._serialized_end=923
  _UCOMMAND._serialized_start=926
  _UCOMMAND._serialized_end=1095
# @@protoc_insertion_point(module_scope)
