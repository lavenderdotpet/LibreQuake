#You should not modify or redistribute this file, as you may break compatibility with future versions of Noesis.
#This module also defines several classes which are integrated with the Noesis native binary Python module, so changing those will cause things to explode.

#There is a lot of instance/type checking in here, because that's just the way things are. You aren't meant to be able to provide custom interfaces for
#these types. If you want to encapsulate them somehow, you should just hold a reference to them in your own custom class/object instead.

import noesis
import struct
import os

#rapi methods should only be used during handler callbacks
import rapi

#in case overriding central unpacking/packing functions becomes desirable
noeUnpack = struct.unpack
noeUnpackFrom = struct.unpack_from
noePack = struct.pack

NOESEEK_ABS = 0
NOESEEK_REL = 1
NOE_BIGENDIAN = 1
NOE_LITTLEENDIAN = 0

#class wrapper to parse through some bytes using the struct unpacker
class NoeUnpacker:
	def __init__(self, data):
		self.byteOfs = 0
		self.data = data
		self.dataSize = len(data)

	def read(self, fmtStr):
		readBytes = struct.calcsize(fmtStr)
		if (self.byteOfs+readBytes) > self.dataSize:
			noesis.doException("Tried to read off end of data array.")
		readData = noeUnpackFrom(fmtStr, self.data, self.byteOfs)
		self.byteOfs += readBytes
		return readData

	def seek(self, addr, isRelative = NOESEEK_ABS):
		if isRelative == NOESEEK_ABS:
			self.byteOfs = addr
		else:
			self.byteOfs += addr
		return self.byteOfs

	def tell(self):
		return self.byteOfs

	def checkOverrun(self, size):
		if self.byteOfs+size > self.dataSize:
			return 1
		return 0


#Universal binary reader/writer, also handles reading/writing data off of byte-aligned boundaries.
#example use:
#	writer = NoeBitStream()
#	writer.writeString("Hello. I'm coming to get you.")
#	open("somefile.bin", "wb").write(writer.getBuffer())
class NoeBitStream(NoeUnpacker):
	def __init__(self, data = None, bigEndian = NOE_LITTLEENDIAN):
		self.data = data
		if data is None: #set up for writing
			self.h = noesis.allocType("writeStream")
		else: #set up for reading
			self.h = noesis.allocType("readStream", self.data)
			self.dataSize = len(self.data)
		self.setEndian(bigEndian)

	def getBuffer(self, startOfs = None, endOfs = None):
		if startOfs is not None and endOfs is not None:
			return noesis.bsGetBufferSlice(self.h, startOfs, endOfs)
		else:
			return noesis.bsGetBuffer(self.h)
	def getSize(self):
		return noesis.bsGetSize(self.h)
	def setOffset(self, ofs):
		noesis.bsSetOfs(self.h, ofs)
	def getOffset(self):
		return noesis.bsGetOfs(self.h)
	def setEndian(self, bigEndian = NOE_LITTLEENDIAN):
		noesis.bsSetEndian(self.h, bigEndian)
	def setByteEndianForBits(self, bigEndian = NOE_LITTLEENDIAN):
		flags = noesis.bsGetFlags(self.h)
		if bigEndian == NOE_LITTLEENDIAN:
			flags &= ~noesis.BITSTREAMFL_DESCENDINGBITS
		else:
			flags |= noesis.BITSTREAMFL_DESCENDINGBITS
		noesis.bsSetFlags(self.h, flags)
	def checkEOF(self):
		return self.getOffset() >= self.getSize()

	def writeBytes(self, data):
		return noesis.bsWriteBytes(self.h, data)
	def writeBits(self, val, numBits):
		return noesis.bsWriteBits(self.h, val, numBits)
	def writeBool(self, val):
		return noesis.bsWriteBool(self.h, val)
	def writeByte(self, val):
		return noesis.bsWriteByte(self.h, val)
	def writeUByte(self, val):
		return noesis.bsWriteUByte(self.h, val)
	def writeShort(self, val):
		return noesis.bsWriteShort(self.h, val)
	def writeUShort(self, val):
		return noesis.bsWriteUShort(self.h, val)
	def writeInt(self, val):
		return noesis.bsWriteInt(self.h, val)
	def writeUInt(self, val):
		return noesis.bsWriteUInt(self.h, val)
	def writeFloat(self, val):
		return noesis.bsWriteFloat(self.h, val)
	def writeDouble(self, val):
		return noesis.bsWriteDouble(self.h, val)
	def writeInt64(self, val):
		return noesis.bsWriteInt64(self.h, val)
	def writeUInt64(self, val):
		return noesis.bsWriteUInt64(self.h, val)
	def writeHalfFloat(self, val):
		return noesis.bsWriteUShort(self.h, noesis.encodeFloat16(val))
	def writeString(self, str, writeTerminator = 1):
		return noesis.bsWriteString(self.h, str, writeTerminator)

	def readBytes(self, numBytes):
		return noesis.bsReadBytes(self.h, numBytes)
	def readBits(self, numBits):
		return noesis.bsReadBits(self.h, numBits)
	def readBool(self):
		return noesis.bsReadBool(self.h)
	def readByte(self):
		return noesis.bsReadByte(self.h)
	def readUByte(self):
		return noesis.bsReadUByte(self.h)
	def readShort(self):
		return noesis.bsReadShort(self.h)
	def readUShort(self):
		return noesis.bsReadUShort(self.h)
	def readInt(self):
		return noesis.bsReadInt(self.h)
	def readUInt(self):
		return noesis.bsReadUInt(self.h)
	def readFloat(self):
		return noesis.bsReadFloat(self.h)
	def readDouble(self):
		return noesis.bsReadDouble(self.h)
	def readInt64(self):
		return noesis.bsReadInt64(self.h)
	def readUInt64(self):
		return noesis.bsReadUInt64(self.h)
	def readUInt24(self):
		return noesis.bsReadUInt24(self.h)
	def readHalfFloat(self):
		return noesis.getFloat16(noesis.bsReadUShort(self.h))
	def readString(self):
		return noesis.bsReadString(self.h)
	def readline(self):
		return noesis.bsReadLine(self.h)

	#provide interfaces for the NoeUnpacker (better to use the base class if you want to use this functionality exclusively)
	def toUnpacker(self):
		self.byteOfs = self.getOffset()
	def fromUnpacker(self):
		self.setOffset(self.byteOfs)
	def read(self, fmtStr):
		self.toUnpacker(); r = noeSuper(self).read(fmtStr); self.fromUnpacker(); return r
	def seek(self, addr, isRelative = NOESEEK_ABS):
		self.toUnpacker(); r = noeSuper(self).seek(addr, isRelative); self.fromUnpacker(); return r
	def tell(self):
		self.toUnpacker(); r = noeSuper(self).tell(); self.fromUnpacker(); return r
	def checkOverrun(self, size):
		self.toUnpacker(); r = noeSuper(self).checkOverrun(size); self.fromUnpacker(); return r

		
#not really fully compatible with NoeBitStream, but may be swapped out in some limited use cases
class NoeFileStream:
	#f should be a file handle which has already been opened
	def __init__(self, f, bigEndian = NOE_LITTLEENDIAN):
		self.f = f
		currentOffset = f.tell()
		f.seek(0, os.SEEK_END)
		self.fileSize = f.tell()
		f.seek(currentOffset, os.SEEK_SET)
		self.setEndian(bigEndian)
	def setEndian(self, bigEndian = NOE_LITTLEENDIAN):
		self.endian = "<" if bigEndian == NOE_LITTLEENDIAN else ">"
		
	def readBytes(self, numBytes):
		return self.f.read(numBytes)
	def readBool(self):
		return self.f.read(1)[0] != 0
	def readByte(self):
		return noeUnpack(self.endian + "b", self.f.read(1))[0]
	def readUByte(self):
		return noeUnpack(self.endian + "B", self.f.read(1))[0]
	def readShort(self):
		return noeUnpack(self.endian + "h", self.f.read(2))[0]
	def readUShort(self):
		return noeUnpack(self.endian + "H", self.f.read(2))[0]
	def readInt(self):
		return noeUnpack(self.endian + "i", self.f.read(4))[0]
	def readUInt(self):
		return noeUnpack(self.endian + "I", self.f.read(4))[0]
	def readFloat(self):
		return noeUnpack(self.endian + "f", self.f.read(4))[0]
	def readDouble(self):
		return noeUnpack(self.endian + "d", self.f.read(8))[0]
	def readInt64(self):
		return noeUnpack(self.endian + "q", self.f.read(8))[0]
	def readUInt64(self):
		return noeUnpack(self.endian + "Q", self.f.read(8))[0]
		
	def seek(self, addr, isRelative = NOESEEK_ABS):
		self.f.seek(addr, os.SEEK_SET if isRelative == NOESEEK_ABS else os.SEEK_CUR)
	def tell(self):
		return self.f.tell()
	def checkEOF(self):
		return self.f.tell() >= self.fileSize
		
#3-component Vector
class NoeVec3:
	def __init__(self, vec3 = (0.0, 0.0, 0.0)):
		self.vec3 = vec3
		noesis.vec3Validate(self)
	def __getitem__(self, index):
		return self.vec3[index]
	def __setitem__(self, index, value):
		if isinstance(self.vec3, tuple):
			self.vec3 = noeTupleToList(self.vec3)
		self.vec3[index] = value
	def __repr__(self):
		return repr(self.vec3)
	def __len__(self):
		return len(self.vec3)
	def binaryCompare(self, other):
		return self.vec3[0] == other.vec3[0] and self.vec3[1] == other.vec3[1] and self.vec3[2] == other.vec3[2]
	def __eq__(self, other):
		return self.binaryCompare(other)
	def __ne__(self, other):
		return not self.binaryCompare(other)

	def __add__(self, other):
		if isinstance(other, (NoeVec3, list, tuple)):
			return noesis.vec3Add(self, other)
		else:
			return NoeVec3([self.vec3[0]+other, self.vec3[1]+other, self.vec3[2]+other])
	def __sub__(self, other):
		if isinstance(other, (NoeVec3, list, tuple)):
			return noesis.vec3Sub(self, other)
		else:
			return NoeVec3([self.vec3[0]-other, self.vec3[1]-other, self.vec3[2]-other])
	def __mul__(self, other):
		if isinstance(other, (NoeVec3, list, tuple)):
			return noesis.vec3Mul(self, other)
		elif isinstance(other, NoeMat43):
			return noesis.mat43TransformPoint(other, self)
		elif isinstance(other, NoeQuat):
			return noesis.quatTransformPoint(other, self)
		else:
			return NoeVec3([self.vec3[0]*other, self.vec3[1]*other, self.vec3[2]*other])
	def __div__(self, other):
		if isinstance(other, (NoeVec3, list, tuple)):
			return noesis.vec3Div(self, other)
		else:
			return NoeVec3([self.vec3[0]/other, self.vec3[1]/other, self.vec3[2]/other])
	def __truediv__(self, other):
		if isinstance(other, (NoeVec3, list, tuple)):
			return noesis.vec3Div(self, other)
		else:
			return NoeVec3([self.vec3[0]/other, self.vec3[1]/other, self.vec3[2]/other])
	def __neg__(self):
		return NoeVec3([-self.vec3[0], -self.vec3[1], -self.vec3[2]])

	def dot(self, other): #returns float
		return noesis.vec3Dot(self, other)
	def cross(self, other): #returns vector
		return noesis.vec3Cross(self, other)
	def length(self): #returns float
		return noesis.vec3Len(self)
	def lengthSq(self): #returns float
		return noesis.vec3LenSq(self)
	def normalize(self): #returns vector
		return noesis.vec3Norm(self)
	def lerp(self, other, fraction): #returns vector
		return noesis.vec3Lerp(self, other, fraction)

	def toAngles(self):
		return noesis.vec3ToAngles(self)
	def toVec4(self):
		return noesis.vec3ToVec4(self)
	def toMat43(self):
		return noesis.vec3ToMat43(self)
	def toAnglesDirect(self):
		return NoeAngles([self.vec3[0], self.vec3[1], self.vec3[2]])
	def toBytes(self): #returns bytearray
		return noesis.vec3ToBytes(self)
	def fromBytes(otherBytes, bigEnd = NOE_LITTLEENDIAN): #returns type built from binary
		return noesis.vec3FromBytes(otherBytes, bigEnd)
	def getStorage(self): #returns raw storage (list, tuple, etc)
		return self.vec3


#4-component Vector
class NoeVec4:
	def __init__(self, vec4 = (0.0, 0.0, 0.0, 0.0)):
		self.vec4 = vec4
		noesis.vec4Validate(self)
	def __getitem__(self, index):
		return self.vec4[index]
	def __setitem__(self, index, value):
		if isinstance(self.vec4, tuple):
			self.vec4 = noeTupleToList(self.vec4)
		self.vec4[index] = value
	def __repr__(self):
		return repr(self.vec4)
	def __len__(self):
		return len(self.vec4)
	def binaryCompare(self, other):
		return self.vec4[0] == other.vec4[0] and self.vec4[1] == other.vec4[1] and self.vec4[2] == other.vec4[2] and self.vec4[3] == other.vec4[3]
	def __eq__(self, other):
		return self.binaryCompare(other)
	def __ne__(self, other):
		return not self.binaryCompare(other)

	def __add__(self, other):
		if isinstance(other, (NoeVec4, list, tuple)):
			return noesis.vec4Add(self, other)
		else:
			return NoeVec4([self.vec4[0]+other, self.vec4[1]+other, self.vec4[2]+other, self.vec4[3]+other])
	def __sub__(self, other):
		if isinstance(other, (NoeVec4, list, tuple)):
			return noesis.vec4Sub(self, other)
		else:
			return NoeVec4([self.vec4[0]-other, self.vec4[1]-other, self.vec4[2]-other, self.vec4[3]-other])
	def __mul__(self, other):
		if isinstance(other, (NoeVec4, list, tuple)):
			return noesis.vec4Mul(self, other)
		elif isinstance(other, NoeMat43):
			return noesis.mat43TransformVec4(other, self)
		elif isinstance(other, NoeMat44):
			return noesis.mat44TransformVec4(other, self)
		else:
			return NoeVec4([self.vec4[0]*other, self.vec4[1]*other, self.vec4[2]*other, self.vec4[3]*other])
	def __div__(self, other):
		if isinstance(other, (NoeVec4, list, tuple)):
			return noesis.vec4Div(self, other)
		else:
			return NoeVec4([self.vec4[0]/other, self.vec4[1]/other, self.vec4[2]/other, self.vec4[3]/other])
	def __truediv__(self, other):
		if isinstance(other, (NoeVec4, list, tuple)):
			return noesis.vec4Div(self, other)
		else:
			return NoeVec4([self.vec4[0]/other, self.vec4[1]/other, self.vec4[2]/other, self.vec4[3]/other])
	def __neg__(self):
		return NoeVec4([-self.vec4[0], -self.vec4[1], -self.vec4[2], -self.vec4[3]])

	def dot(self, other): #returns float
		return noesis.vec4Dot(self, other)
	def length(self): #returns float
		return noesis.vec4Len(self)
	def lengthSq(self): #returns float
		return noesis.vec4LenSq(self)
	def normalize(self): #returns vector
		return noesis.vec4Norm(self)
	def lerp(self, other, fraction): #returns vector
		return noesis.vec4Lerp(self, other, fraction)

	def toVec3(self):
		return noesis.vec4ToVec3(self)
	def toBytes(self): #returns bytearray
		return noesis.vec4ToBytes(self)
	def fromBytes(otherBytes, bigEnd = NOE_LITTLEENDIAN): #returns type built from binary
		return noesis.vec4FromBytes(otherBytes, bigEnd)
	def getStorage(self): #returns raw storage (list, tuple, etc)
		return self.vec4


#Euler angles (can and occasionally is also used to store radians, see also noesis.g_flDegToRad/noesis.g_flRadToDeg constants)
class NoeAngles:
	def __init__(self, angles = (0.0, 0.0, 0.0)):
		self.vec3 = angles
		noesis.anglesValidate(self)
	def __getitem__(self, index):
		return self.vec3[index]
	def __setitem__(self, index, value):
		if isinstance(self.vec3, tuple):
			self.vec3 = noeTupleToList(self.vec3)
		self.vec3[index] = value
	def __repr__(self):
		return repr(self.vec3)
	def __len__(self):
		return len(self.vec3)
	def binaryCompare(self, other):
		return self.vec3[0] == other.vec3[0] and self.vec3[1] == other.vec3[1] and self.vec3[2] == other.vec3[2]
	def __eq__(self, other):
		return self.binaryCompare(other)
	def __ne__(self, other):
		return not self.binaryCompare(other)

	def __add__(self, other):
		if isinstance(other, (NoeAngles, NoeVec3, list, tuple)):
			return noesis.vec3Add(self, other).toAnglesDirect()
		else:
			return NoeAngles([self.vec3[0]+other, self.vec3[1]+other, self.vec3[2]+other])
	def __sub__(self, other):
		if isinstance(other, (NoeAngles, NoeVec3, list, tuple)):
			return noesis.vec3Sub(self, other).toAnglesDirect()
		else:
			return NoeAngles([self.vec3[0]-other, self.vec3[1]-other, self.vec3[2]-other])
	def __mul__(self, other):
		if isinstance(other, (NoeAngles, NoeVec3, list, tuple)):
			return noesis.vec3Mul(self, other).toAnglesDirect()
		else:
			return NoeAngles([self.vec3[0]*other, self.vec3[1]*other, self.vec3[2]*other])
	def __div__(self, other):
		if isinstance(other, (NoeAngles, NoeVec3, list, tuple)):
			return noesis.vec3Div(self, other).toAnglesDirect()
		else:
			return NoeAngles([self.vec3[0]/other, self.vec3[1]/other, self.vec3[2]/other])
	def __truediv__(self, other):
		if isinstance(other, (NoeAngles, NoeVec3, list, tuple)):
			return noesis.vec3Div(self, other).toAnglesDirect()
		else:
			return NoeAngles([self.vec3[0]/other, self.vec3[1]/other, self.vec3[2]/other])
	def __neg__(self):
		return NoeAngles([-self.vec3[0], -self.vec3[1], -self.vec3[2]])

	def angleMod(self, f): #returns angles
		return noesis.anglesMod(self, f)
	def normalize180(self): #returns angles
		return noesis.anglesNormalize180(self)
	def normalize360(self): #returns angles
		return noesis.anglesNormalize360(self)
	def angleVectors(self): #returns mat43
		return noesis.anglesAngleVectors(self)
	def lerp(self, other, fraction): #returns angles
		return noesis.vec3Lerp(self, other, fraction).toAnglesDirect()
	def alerp(self, other, degrees): #returns angles
		return noesis.anglesALerp(self, other, degrees)

	#all "to" functions assume angles are in degrees and not radians.
	def toVec3(self):
		return noesis.anglesToVec3(self)
	def toMat43(self):
		return noesis.anglesToMat43(self)
	def toMat43_XYZ(self, yFlip = 1):
		return noesis.anglesToMat43_XYZ(self, yFlip)
	def toMat43_ArbConv(self, axes = (2, 1, 0), oris = (1.0, -1.0, 1.0)):
		rotMat = NoeMat43()
		v = NoeVec3([0.0, 0.0, 0.0])
		v.vec3[axes[0]] = oris[0]
		rotMat = rotMat.rotate(self.vec3[axes[0]], v)
		v = NoeVec3([0.0, 0.0, 0.0])
		v.vec3[axes[1]] = oris[1]
		rotMat = rotMat.rotate(self.vec3[axes[1]], v)
		v = NoeVec3([0.0, 0.0, 0.0])
		v.vec3[axes[2]] = oris[2]
		rotMat = rotMat.rotate(self.vec3[axes[2]], v)
		return rotMat
	def toQuat(self):
		return noesis.anglesToQuat(self)
	def toVec3Direct(self):
		return NoeVec3([self.vec3[0], self.vec3[1], self.vec3[2]])
	def toRadians(self):
		return NoeAngles([self.vec3[0]*noesis.g_flDegToRad, self.vec3[1]*noesis.g_flDegToRad, self.vec3[2]*noesis.g_flDegToRad])
	def toDegrees(self):
		return NoeAngles([self.vec3[0]*noesis.g_flRadToDeg, self.vec3[1]*noesis.g_flRadToDeg, self.vec3[2]*noesis.g_flRadToDeg])
	def toBytes(self): #returns bytearray
		return noesis.vec3ToBytes(self)
	def fromBytes(otherBytes, bigEnd = NOE_LITTLEENDIAN): #returns type built from binary
		return NoeAngles(noesis.vec3FromBytes(otherBytes, bigEnd).vec3)
	def getStorage(self): #returns raw storage (list, tuple, etc)
		return self.vec3


identityMat43Tuple = ( NoeVec3((1.0, 0.0, 0.0)), NoeVec3((0.0, 1.0, 0.0)), NoeVec3((0.0, 0.0, 1.0)), NoeVec3((0.0, 0.0, 0.0)) )
identityMat44Tuple = ( NoeVec4((1.0, 0.0, 0.0, 0.0)), NoeVec4((0.0, 1.0, 0.0, 0.0)), NoeVec4((0.0, 0.0, 1.0, 0.0)), NoeVec4((0.0, 0.0, 0.0, 1.0)) )


#4x3 matrix
class NoeMat43:
	def __init__(self, mat43 = identityMat43Tuple):
		self.mat43 = mat43
		noesis.mat43Validate(self)
	def __getitem__(self, index):
		return self.mat43[index]
	def __setitem__(self, index, value):
		if isinstance(self.mat43, tuple):
			self.mat43 = noeTupleToList(self.mat43)
		self.mat43[index] = value
	def __repr__(self):
		return repr(self.mat43)
	def __len__(self):
		return len(self.mat43)
	def binaryCompare(self, other):
		return self.mat43[0] == other.mat43[0] and self.mat43[1] == other.mat43[1] and self.mat43[2] == other.mat43[2] and self.mat43[3] == other.mat43[3]
	def __eq__(self, other):
		return self.binaryCompare(other)
	def __ne__(self, other):
		return not self.binaryCompare(other)

	def __add__(self, other):
		return noesis.mat43Add(self, other)
	def __sub__(self, other):
		return noesis.mat43Sub(self, other)
	def __mul__(self, other):
		if isinstance(other, (NoeMat43, list, tuple)):
			return noesis.mat43Mul(self, other)
		elif isinstance(other, NoeVec3):
			return noesis.mat43TransformPoint(self, other)
		elif isinstance(other, NoeVec4):
			return noesis.mat43TransformVec4(self, other)
		else:
			return NoeMat43([self.mat43[0]*other, self.mat43[1]*other, self.mat43[2]*other, self.mat43[3]*other])
	def __neg__(self):
		return NoeMat43([-self.mat43[0], -self.mat43[1], -self.mat43[2], -self.mat43[3]])

	def transformPoint(self, other): #returns vec3
		return noesis.mat43TransformPoint(self, other)
	def transformNormal(self, other): #returns vec3
		return noesis.mat43TransformNormal(self, other)
	def transformVec4(self, other): #returns vec4
		return noesis.mat43TransformVec4(self, other)
	def transpose(self): #returns mat43
		return noesis.mat43Transpose(self)
	def inverse(self): #returns mat43
		return noesis.mat43Inverse(self)
	def orthogonalize(self): #returns mat43
		return noesis.mat43Orthogonalize(self)
	def isSkewed(self): #returns 1 if skewed, otherwise 0
		return noesis.mat43IsSkewed(self)
	def rotate(self, degrees, rotAngles, transposeRot = 0): #returns mat43
		return noesis.mat43Rotate(self, degrees, rotAngles, transposeRot)
	def translate(self, trnVector): #returns mat43
		return noesis.mat43Translate(self, trnVector)
	def lerp(self, other, fraction): #returns mat43
		return noesis.mat43Lerp(self, other, fraction)
	def slerp(self, other, fraction): #returns mat43
		return noesis.mat43SLerp(self, other, fraction)
	def swapHandedness(self, axis = 0): #returns mat43
		return noesis.mat43SwapHandedness(self, axis)

	def toQuat(self):
		return noesis.mat43ToQuat(self)
	def toAngles(self):
		return noesis.mat43ToAngles(self)
	def toMat44(self):
		return noesis.mat43ToMat44(self)
	def toBytes(self): #returns bytearray
		return noesis.mat43ToBytes(self)
	def fromBytes(otherBytes, bigEnd = NOE_LITTLEENDIAN): #returns type built from binary
		return noesis.mat43FromBytes(otherBytes, bigEnd)
	def getStorage(self): #returns raw storage (list, tuple, etc)
		return self.mat43


#4x4 matrix
#NoeMat44 operations (including to and from NoeMat43) have rows and columns swapped
class NoeMat44:
	def __init__(self, mat44 = identityMat44Tuple):
		self.mat44 = mat44
		noesis.mat44Validate(self)
	def __getitem__(self, index):
		return self.mat44[index]
	def __setitem__(self, index, value):
		if isinstance(self.mat44, tuple):
			self.mat44 = noeTupleToList(self.mat44)
		self.mat44[index] = value
	def __repr__(self):
		return repr(self.mat44)
	def __len__(self):
		return len(self.mat44)
	def binaryCompare(self, other):
		return self.mat44[0] == other.mat44[0] and self.mat44[1] == other.mat44[1] and self.mat44[2] == other.mat44[2] and self.mat44[3] == other.mat44[3]
	def __eq__(self, other):
		return self.binaryCompare(other)
	def __ne__(self, other):
		return not self.binaryCompare(other)

	def __add__(self, other):
		return noesis.mat44Add(self, other)
	def __sub__(self, other):
		return noesis.mat44Sub(self, other)
	def __mul__(self, other):
		if isinstance(other, (NoeMat44, list, tuple)):
			return noesis.mat44Mul(self, other)
		elif isinstance(other, NoeVec4):
			return noesis.mat44TransformVec4(self, other)
		else:
			return NoeMat44([self.mat44[0]*other, self.mat44[1]*other, self.mat44[2]*other, self.mat44[3]*other])
	def __neg__(self):
		return NoeMat44([-self.mat44[0], -self.mat44[1], -self.mat44[2], -self.mat44[3]])

	def transformVec4(self, other): #returns vec4
		return noesis.mat44TransformVec4(self, other)
	def transpose(self): #returns mat44
		return noesis.mat44Transpose(self)
	def inverse(self): #returns mat44
		return noesis.mat44Inverse(self)
	def rotate(self, degrees, rotAngles): #returns mat44
		return noesis.mat44Rotate(self, degrees, rotAngles)
	def translate(self, trnVector): #returns mat44
		return noesis.mat44Translate(self, trnVector)
	def swapHandedness(self, axis = 0): #returns mat44
		return noesis.mat44SwapHandedness(self, axis)
		
	def toMat43(self):
		return noesis.mat44ToMat43(self)
	def toBytes(self): #returns bytearray
		return noesis.mat44ToBytes(self)
	def fromBytes(otherBytes, bigEnd = NOE_LITTLEENDIAN): #returns type built from binary
		return noesis.mat44FromBytes(otherBytes, bigEnd)
	def getStorage(self): #returns raw storage (list, tuple, etc)
		return self.mat44


#packed quaternion
class NoeQuat3:
	def __init__(self, quat3 = (0.0, 0.0, 0.0)):
		self.vec3 = quat3
		noesis.quat3Validate(self)
	def __getitem__(self, index):
		return self.vec3[index]
	def __setitem__(self, index, value):
		if isinstance(self.vec3, tuple):
			self.vec3 = noeTupleToList(self.vec3)
		self.vec3[index] = value
	def __repr__(self):
		return repr(self.vec3)
	def __len__(self):
		return len(self.vec3)
	def binaryCompare(self, other):
		return self.vec3[0] == other.vec3[0] and self.vec3[1] == other.vec3[1] and self.vec3[2] == other.vec3[2]
	def __eq__(self, other):
		return self.binaryCompare(other)
	def __ne__(self, other):
		return not self.binaryCompare(other)

	def toQuat(self):
		return noesis.quat3ToQuat(self)
	def toBytes(self): #returns bytearray
		return noesis.quat3ToBytes(self)
	def fromBytes(otherBytes, bigEnd = NOE_LITTLEENDIAN): #returns type built from binary
		return noesis.quat3FromBytes(otherBytes, bigEnd)
	def getStorage(self): #returns raw storage (list, tuple, etc)
		return self.vec3


#quaternion
class NoeQuat:
	def __init__(self, quat = (0.0, 0.0, 0.0, 1.0)):
		self.quat = quat
		noesis.quatValidate(self)
	def __getitem__(self, index):
		return self.quat[index]
	def __setitem__(self, index, value):
		if isinstance(self.quat, tuple):
			self.quat = noeTupleToList(self.quat)
		self.quat[index] = value
	def __repr__(self):
		return repr(self.quat)
	def __len__(self):
		return len(self.quat)
	def binaryCompare(self, other):
		return self.quat[0] == other.quat[0] and self.quat[1] == other.quat[1] and self.quat[2] == other.quat[2] and self.quat[3] == other.quat[3]
	def __eq__(self, other):
		return self.binaryCompare(other)
	def __ne__(self, other):
		return not self.binaryCompare(other)

	def __add__(self, other):
		if isinstance(other, (NoeQuat, NoeVec4, list, tuple)):
			return noesis.quatAdd(self, other)
		else:
			return NoeQuat([self.quat[0]+other, self.quat[1]+other, self.quat[2]+other, self.quat[3]+other])
	def __sub__(self, other):
		if isinstance(other, (NoeQuat, NoeVec4, list, tuple)):
			return noesis.quatSub(self, other)
		else:
			return NoeQuat([self.quat[0]-other, self.quat[1]-other, self.quat[2]-other, self.quat[3]-other])
	def __mul__(self, other):
		if isinstance(other, (NoeQuat, list, tuple)):
			return noesis.quatMul(self, other)
		elif isinstance(other, NoeVec3):
			return noesis.quatTransformPoint(self, other)
		else:
			return NoeQuat([self.quat[0]*other, self.quat[1]*other, self.quat[2]*other, self.quat[3]*other])
	def __neg__(self):
		return NoeQuat([-self.quat[0], -self.quat[1], -self.quat[2], -self.quat[3]])

	def transformPoint(self, other): #returns vec3
		return noesis.quatTransformPoint(self, other)
	def transformNormal(self, other): #returns vec3
		return noesis.quatTransformNormal(self, other)
	def transpose(self): #returns quat
		return noesis.quatTranspose(self)
	def length(self): #returns float
		return noesis.quatLen(self)
	def normalize(self): #returns quat
		return noesis.quatNormalize(self)
	def lerp(self, other, fraction): #returns quat
		return noesis.quatLerp(self, other, fraction)
	def slerp(self, other, fraction): #returns quat
		return noesis.quatSLerp(self, other, fraction)

	def toQuat3(self):
		return noesis.quatToQuat3(self)
	def toMat43(self, transposed = 0):
		return noesis.quatToMat43(self, transposed)
	def toMatAngles(self):
		return noesis.quatToAngles(self)
	def toBytes(self): #returns bytearray
		return noesis.quatToBytes(self)
	def fromBytes(otherBytes, bigEnd = NOE_LITTLEENDIAN): #returns type built from binary
		return noesis.quatFromBytes(otherBytes, bigEnd)
	def getStorage(self): #returns raw storage (list, tuple, etc)
		return self.quat


#texture object
#for supported pixel types, look at constants exposed by noesis module, such as NOESISTEX_RGB24, NOESISTEX_RGBA32, NOESISTEX_DXT1, etc.
class NoeTexture:
	def __init__(self, name, width, height, pixelData, pixelType = noesis.NOESISTEX_RGBA32):
		self.name = name
		self.width = width
		self.height = height
		self.pixelData = pixelData
		self.pixelType = pixelType
		self.flags = 0
		self.mipCount = 0
	def __repr__(self):
		return "(NoeTexture:" + " w:" + repr(self.width) + " h:" + repr(self.height) + " p:" + repr(self.pixelType) + " f:" + repr(self.flags) + " n:" + repr(self.name) + ")"

	def setFlags(self, flags):
		self.flags = flags

	def setMipCount(self, mipCount):
		self.mipCount = mipCount


#material object
class NoeMaterial:
	def __init__(self, name, texName):
		self.name = name
		self.setTexture(texName)
		self.setFlags(0)
		self.setFlags2(0)

	#texture names must match the name of a texture in the corresponding texture list to be applied
	def setTexture(self, texName):
		self.texName = texName

	def setNormalTexture(self, texName):
		self.nrmTexName = texName

	def setSpecularTexture(self, texName):
		self.specTexName = texName

	def setOpacityTexture(self, texName):
		self.opacTexName = texName

	def setBumpTexture(self, texName):
		self.bumpTexName = texName

	def setEnvTexture(self, texName):
		self.envTexName = texName

	def setOcclTexture(self, texName):
		self.occlTexName = texName
		
	def setFlags(self, flags, disableLighting = 0):
		self.flags = flags
		self.disableLighting = disableLighting

	def setFlags2(self, flags2):
		self.flags2 = flags2
		
	def setSkipRender(self, skipRender):
		self.skipRender = skipRender

	#uses gl blend string names (GL_ONE, GL_SRC_COLOR, etc)
	def setBlendMode(self, blendSrc, blendDst):
		self.blendSrc = blendSrc
		self.blendDst = blendDst

	#enables/disables default blending
	def setDefaultBlend(self, defaultBlend):
		self.defaultBlend = defaultBlend

	def setAlphaTest(self, alphaVal):
		self.alphaTest = alphaVal

	def setDiffuseColor(self, clr = NoeVec4([1.0, 1.0, 1.0, 1.0])):
		self.diffuseColor = clr

	#4th component is the exponent
	def setSpecularColor(self, clr = NoeVec4([1.0, 1.0, 1.0, 8.0])):
		self.specularColor = clr

	def setAmbientColor(self, clr = NoeVec4([0.0, 0.0, 0.0, 0.0])):
		self.ambientColor = clr

	#4th component is fresnel term scale
	def setEnvColor(self, clr = NoeVec4([1.0, 1.0, 1.0, 0.8])):
		self.envColor = clr
		
	def setRimLighting(self, rimColor = NoeVec3([1.0, 1.0, 1.0]), rimSize = 1.0, rimPow = 3.0, rimBias = 0.0, rimOfs = NoeVec3([0.0, 0.0, 0.0])):
		self.rimColor = rimColor
		self.rimSize = rimSize
		self.rimPow = rimPow
		self.rimBias = rimBias
		self.rimOfs = rimOfs
		
	def setRoughness(self, roughnessScale, roughnessBias):
		self.roughnessScale = roughnessScale
		self.roughnessBias = roughnessBias

	def setMetal(self, metalScale, metalBias):
		self.metalScale = metalScale
		self.metalBias = metalBias

	def setAnisotropy(self, anisoScale, anisoAngle):
		self.anisoScale = anisoScale
		self.anisoAngle = anisoAngle
		
	def setSpecularSwizzle(self, specularSwizzle):
		self.specularSwizzle = specularSwizzle
		
	def setNextPass(self, nextPass):
		self.nextPass = nextPass
		
	def setUserData(self, userTag, userData):
		if len(userTag) != 8:
			print("WARNING: Call to setUserData ignored, userTag should be an 8-byte unique id.")
		else:
			self.userTag = userTag
			self.userData = userData
		
	#sets expression strings. see pluginshare.h for a list of expression functions and variables.
	def setExpr_vpos_x(self, exprStr):
		self.expr_vpos_x = exprStr
	def setExpr_vpos_y(self, exprStr):
		self.expr_vpos_y = exprStr
	def setExpr_vpos_z(self, exprStr):
		self.expr_vpos_z = exprStr
	def setExpr_vnrm_x(self, exprStr):
		self.expr_vnrm_x = exprStr
	def setExpr_vnrm_y(self, exprStr):
		self.expr_vnrm_y = exprStr
	def setExpr_vnrm_z(self, exprStr):
		self.expr_vnrm_z = exprStr
	def setExpr_vuv_u(self, exprStr):
		self.expr_vuv_u = exprStr
	def setExpr_vuv_v(self, exprStr):
		self.expr_vuv_v = exprStr
	def setExpr_vclr_r(self, exprStr):
		self.expr_vclr_r = exprStr
	def setExpr_vclr_g(self, exprStr):
		self.expr_vclr_g = exprStr
	def setExpr_vclr_b(self, exprStr):
		self.expr_vclr_b = exprStr
	def setExpr_vclr_a(self, exprStr):
		self.expr_vclr_a = exprStr
	def setExpr_diffuse_r(self, exprStr):
		self.expr_diffuse_r = exprStr
	def setExpr_diffuse_g(self, exprStr):
		self.expr_diffuse_g = exprStr
	def setExpr_diffuse_b(self, exprStr):
		self.expr_diffuse_b = exprStr
	def setExpr_diffuse_a(self, exprStr):
		self.expr_diffuse_a = exprStr
	def setExpr_specular_r(self, exprStr):
		self.expr_specular_r = exprStr
	def setExpr_specular_g(self, exprStr):
		self.expr_specular_g = exprStr
	def setExpr_specular_b(self, exprStr):
		self.expr_specular_b = exprStr
	def setExpr_specular_exp(self, exprStr):
		self.expr_specular_exp = exprStr
	def setExpr_uvtrans_x(self, exprStr):
		self.expr_uvtrans_x = exprStr
	def setExpr_uvtrans_y(self, exprStr):
		self.expr_uvtrans_y = exprStr
	def setExpr_uvtrans_z(self, exprStr):
		self.expr_uvtrans_z = exprStr
	def setExpr_uvrot_x(self, exprStr):
		self.expr_uvrot_x = exprStr
	def setExpr_uvrot_y(self, exprStr):
		self.expr_uvrot_y = exprStr
	def setExpr_uvrot_z(self, exprStr):
		self.expr_uvrot_z = exprStr
	def setExpr_texidx(self, exprStr):
		self.expr_texidx = exprStr
	def setExpr_normaltexidx(self, exprStr):
		self.expr_normaltexidx = exprStr
	def setExpr_speculartexidx(self, exprStr):
		self.expr_speculartexidx = exprStr

		
#material and texture lists must be provided to the Noesis API in one of these containers (for the purpose of possible future extension)
class NoeModelMaterials:
	#must be initialized with lists of NoeTexture and NoeMaterial
	def __init__(self, texList, matList):
		noesis.validateListType(texList, NoeTexture)
		noesis.validateListType(matList, NoeMaterial)
		self.matList = matList
		self.texList = texList


#model bone. bone hierarchy is defined by matching bone name to parentName.
#index is used to ensure order and match to vertex weights. it is possible to have gaps in your bone list by specifying out-of-order indices.
#NOTE: you don't need to specify parentIndex as long as you specify parentName. parentIndex is optional.
class NoeBone:
	def __init__(self, index, name, matrix, parentName = None, parentIndex = -1):
		self.index = index
		self.name = name
		self.setMatrix(matrix)
		self.parentName = parentName
		self.parentIndex = parentIndex #parent index may be specified instead of parentName, if it's more convenient. this is an index corresponding to self.index, and not the position in the list.
	def __repr__(self):
		return "(NoeBone:" + repr(self.index) + "," + self.name + "," + repr(self.parentName) + "," + repr(self.parentIndex) + ")"

	def setMatrix(self, matrix):
		if not isinstance(matrix, NoeMat43):
			noesis.doException("Invalid type provided for bone matrix")
		self._matrix = matrix
	def getMatrix(self):
		return self._matrix


#keyframe data type
class NoeKeyFramedValue:
	#value may be NoeQuat, NoeVec3, float, etc. depending on the data type specified
	def __init__(self, time, value):
		self.time = time
		self.value = value
		self.componentIndex = 0
	def __repr__(self):
		return "NoeKFVal(time:" + repr(self.time) + " value:" + repr(self.value) + ")"
		
	def setComponentIndex(self, componentIndex):
		self.componentIndex = componentIndex


#keyframed bone class
class NoeKeyFramedBone:
	def __init__(self, boneIndex):
		self.boneIndex = boneIndex
		self.setRotation([])
		self.setTranslation([])
		self.setScale([])
		
	#for the set methods, keys should be a list of NoeKeyFramedValue or an object with similarly available members
	def setRotation(self, keys, type = noesis.NOEKF_ROTATION_QUATERNION_4, interpolationType = noesis.NOEKF_INTERPOLATE_LINEAR):
		self.rotationKeys = keys
		self.rotationType = type
		self.rotationInterpolation = interpolationType
	def setTranslation(self, keys, type = noesis.NOEKF_TRANSLATION_VECTOR_3, interpolationType = noesis.NOEKF_INTERPOLATE_LINEAR):
		self.translationKeys = keys
		self.translationType = type
		self.translationInterpolation = interpolationType
	def setScale(self, keys, type = noesis.NOEKF_SCALE_SCALAR_1, interpolationType = noesis.NOEKF_INTERPOLATE_LINEAR):
		self.scaleKeys = keys
		self.scaleType = type
		self.scaleInterpolation = interpolationType


#keyframed animation class
class NoeKeyFramedAnim:
	def __init__(self, name, bones, kfBones, frameRate = 20.0, flags = 0):
		noesis.validateListType(bones, NoeBone)
		noesis.validateListType(kfBones, NoeKeyFramedBone)
		self.name = name
		self.bones = bones
		self.kfBones = kfBones
		self.frameRate = frameRate
		self.flags = flags
	def __repr__(self):
		return "(NoeKFAnim:" + self.name + ")"


#main animation class
#bones must be a list of NoeBone objects, frameMats must be a flat list of NoeMat43 objects
class NoeAnim:
	def __init__(self, name, bones, numFrames, frameMats, frameRate = 20.0, flags = 0):
		noesis.validateListType(bones, NoeBone)
		noesis.validateListType(frameMats, NoeMat43)
		self.name = name
		self.bones = bones
		self.numFrames = numFrames
		self.frameMats = frameMats
		self.setFrameRate(frameRate)
		self.flags = flags
	def __repr__(self):
		return "(NoeAnim:" + self.name + "," + repr(self.numFrames) + "," + repr(self.frameRate) + ")"

	def setFrameRate(self, frameRate):
		self.frameRate = frameRate


#procedural animation object - specifies some parameters which can be baked into an animation using createProceduralAnim
class NoeProceduralAnim:
	def __init__(self, boneName, angleAmount, axis, timeScale):
		self.setBoneName(boneName)
		self.setAngleAmount(angleAmount)
		self.setAxis(axis)
		self.setTimeScale(timeScale)
	def setBoneName(self, boneName): #string matching this procedural anim object to a bone
		self.boneName = boneName
	def setAngleAmount(self, angleAmount): #maximum sway degrees
		self.angleAmount = angleAmount
	def setAxis(self, axis): #axis of rotation (int, 0-2)
		self.axis = axis
	def setTimeScale(self, timeScale): #time multiplier for the duration of the animation
		self.timeScale = timeScale


#user stream class - arbitrary user-named streams of vertex data
class NoeUserStream:
	def __init__(self, name, data, elemSize, flags):
		self.name = name
		self.data = data
		self.elemSize = elemSize
		self.flags = flags
	def __repr__(self):
		return "(NoeUserStream:" + self.name + "," + repr(len(self.data)) + "," + repr(self.elemSize) + "," + repr(self.flags) + ")"


#main mesh class
#all vertex types (positions, normals, uv's, etc) are expected to match in count, as they all share a single triangle list.
#it's recommended that you use the rapi.rpg interface if you want a convenient means to convert different data/primitive types into a NoeModel with NoeMeshes.
class NoeMesh:
	def __init__(self, triList, posList, name = "default", materialName = "default", glbVertIdx = -1, glbTriIdx = -1):
		self.setIndices(triList)
		self.setPositions(posList)
		self.setName(name)
		self.setMaterial(materialName)
		#glb's are indices into the parent model's globalVtx/globalIdx lists on export
		self.setPrimGlobals(glbVertIdx, glbTriIdx)
		self.setLightmap("")
		self.setTransformedVerts(None, None)
		#fill in placeholders
		self.setNormals([])
		self.setUVs([])
		self.setUVs([], 1)
		self.uvxList = []
		self.setTangents([])
		self.setTangents([], 1)
		self.setColors([])
		self.setWeights([])
		self.setMorphList([])
		self.setBoneMap([])
		self.setUserStreams([])
		self.texRefIndex = -1 #this is set by Noesis internally when you load a model's textures manually

	def __repr__(self):
		return "(NoeMesh:" + self.name + "," + self.matName + "," + repr(len(self.indices)) + "," + repr(len(self.positions)) + ")"

	def setName(self, name):
		self.name = name

	def setMaterial(self, materialName):
		self.matName = materialName

	#triangle lists are single-dimension lists of ints, expected to be divisible by 3
	def setIndices(self, triList):
		self.indices = triList

	def setPositions(self, posList):
		noesis.validateListType(posList, NoeVec3)
		self.positions = posList

	def setNormals(self, nrmList):
		noesis.validateListType(nrmList, NoeVec3)
		self.normals = nrmList

	#uv z component should typically be 0
	def setUVs(self, uvList, slot = 0):
		noesis.validateListType(uvList, NoeVec3)
		if slot == 0:
			self.uvs = uvList
		elif slot == 1:
			self.lmUVs = uvList
		else:
			uvxIndex = slot - 2
			d = uvxIndex - len(self.uvxList)
			if d >= 0:
				self.uvxList += [None] * (d + 1)
			self.uvxList[uvxIndex] = uvList

	#translation component of NoeMat43 is ignored for tangents (matrix[0]=normal, matrix[1]=tangent, matrix[2]=bitangent)
	def setTangents(self, tanList, slot = 0):
		noesis.validateListType(tanList, NoeMat43)
		if slot == 0:
			self.tangents = tanList
		elif slot == 1:
			self.lmTangents = tanList
		else:
			noesis.doException("Unsupported tangent slot")

	#color lists are rgba values stored in vec4's
	def setColors(self, clrList):
		noesis.validateListType(clrList, NoeVec4)
		self.colors = clrList

	def setWeights(self, weightList):
		noesis.validateListType(weightList, NoeVertWeight)
		self.weights = weightList

	def setMorphList(self, morphList):
		noesis.validateListType(morphList, NoeMorphFrame)
		self.morphList = morphList

	def setBoneMap(self, boneMap):
		self.boneMap = boneMap
		
	def setUserStreams(self, userStreamList):
		noesis.validateListType(userStreamList, NoeUserStream)		
		self.userStreams = userStreamList

	#indices into the parent model's globalVtx/globalIdx lists on export
	def setPrimGlobals(self, glbVertIdx, glbTriIdx):
		self.glbVertIdx = glbVertIdx
		self.glbTriIdx = glbTriIdx

	def setLightmap(self, lmMatName):
		self.lmMatName = lmMatName

	def setSourceName(self, sourceName):
		self.sourceName = sourceName
		
	#not currently used, planned in a future update
	def setTransformedVerts(self, positions, normals):
		self.transVerts = positions
		self.transNormals = normals

	#convenience function for checking if vertex components have valid content
	def componentEmpty(component):
		if component is None or len(component) <= 0:
			return 1
		return 0


#vertex weight. number of indices and weights should match.
class NoeVertWeight:
	def __init__(self, indices, weights):
		self.indices = indices
		self.weights = weights

	def numWeights(self):
		n = len(self.indices)
		if n != len(self.weights):
			noesis.doException("Weight without matching index/value length")
		return n


#vertex morph frame - represents a single frame of vertex morph animation
#note that it is valid for normals to be None (some models only want to provide positions for vertex anims), but positions should always be a valid list.
#a vertex morph frame should always have as many entries in its vertex lists as other vertex components in the mesh it belongs to.
class NoeMorphFrame:
	def __init__(self, positions, normals):
		noesis.validateListType(positions, NoeVec3)
		noesis.validateListType(normals, NoeVec3)
		self.positions = positions
		self.normals = normals


#global vertex which references per-mesh data
class NoeGlobalVert:
	def __init__(self, meshIndex, vertIndex):
		self.meshIndex = meshIndex
		self.vertIndex = vertIndex


#main model class
class NoeModel:
	def __init__(self, meshes = [], bones = [], anims = [], modelMats = None):
		self.setMeshes(meshes)
		self.setBones(bones)
		self.setAnims(anims)
		self.setModelMaterials(modelMats)
		self.setPrimGlobals(None, None)

	def setModelMaterials(self, modelMats):
		if modelMats is not None and not isinstance(modelMats, NoeModelMaterials):
			noesis.doException("Invalid type provided for model materials")
		self.modelMats = modelMats

	#animations will be applied to the model based on matching bone names from their local bone lists
	def setAnims(self, anims):
		noesis.validateListTypes(anims, (NoeAnim, NoeKeyFramedAnim))
		self.anims = anims

	def setMeshes(self, meshes):
		noesis.validateListType(meshes, NoeMesh)
		self.meshes = meshes

	def setBones(self, bones):
		noesis.validateListType(bones, NoeBone)
		self.bones = bones

	#note that globalVtx/Idx are ignored by Noesis (only mesh geometry is used), but are provided for convenience when exporting
	def setPrimGlobals(self, globalVtx, globalIdx):
		self.globalVtx = globalVtx #list of NoeGlobalVert
		self.globalIdx = globalIdx #triangle index (int) list referencing globalVtx


#spline knot
class NoeSplineKnot:
	def __init__(self, pos, inVec, outVec):
		self.pos = pos
		self.inVec = inVec
		self.outVec = outVec

	def __repr__(self):
		return noeCFloatRepr(self.pos) + ", " + noeCFloatRepr(self.inVec) + ", " + noeCFloatRepr(self.outVec)


#spline
class NoeSpline:
	def __init__(self, knots, mins, maxs, flags):
		self.knots = knots
		if mins is None or maxs is None:
			knot = knots[0] if len(knots) > 0 else NoeSplineKnot([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
			self.mins = [knot.pos[0], knot.pos[1], knot.pos[2]]
			self.maxs = [knot.pos[0], knot.pos[1], knot.pos[2]]
			for i in range(1, len(knots)):
				knot = knots[i]
				for j in range(0, 3):
					self.mins[j] = min(self.mins[j], knot.pos[j])
					self.maxs[j] = max(self.maxs[j], knot.pos[j])
		else:
			self.mins = mins
			self.maxs = maxs
		self.flags = flags

	def getLastOut(self, index):
		if index > 0:
			return self.knots[index-1].outVec
		if self.flags & noesis.NOESPLINEFLAG_CLOSED:
			return self.knots[len(self.knots)-1].outVec
		return self.knots[index].inVec
		
	def getLastPos(self, index):
		if index > 0:
			return self.knots[index-1].pos
		if self.flags & noesis.NOESPLINEFLAG_CLOSED:
			return self.knots[len(self.knots)-1].pos
		return self.knots[index].inVec

	def plotPoints(self, step, plotFunction):
		for i in range(0, len(self.knots)):
			knot = self.knots[i]
			points = (self.getLastPos(i), self.getLastOut(i), knot.inVec, knot.pos)
			frac = 0.0
			while frac < 1.0:
				plotFunction(self, noesis.cubicBezier3D(points, frac), frac)
				frac += step


#spline set
class NoeSplineSet:
	def __init__(self, splines, mins, maxs):
		self.splines = splines
		self.mins = mins
		self.maxs = maxs


#returned in a list by unpackPS2VIF
class NoePS2VIFUnpack:
	def __init__(self, data, numElems, elemBits):
		self.data = data
		self.numElems = numElems
		self.elemBits = elemBits

	def __repr__(self):
		return "NoePS2VIFUnpack(numElems:" + repr(self.numElems) + ",elemBits:" + repr(self.elemBits) + ",datasize:" + repr(len(self.data)) + ")"


#returned by decodePSPVert
class NoePSPVert:
	def __init__(self, vertexDict):
		#posType:
		#0 == none
		#1 == 3 signed bytes
		#2 == 3 signed shorts
		#3 == 3 floats
		#normalType:
		#0 == none
		#1 == 3 signed bytes
		#2 == 3 signed shorts
		#3 == 3 floats
		#uvType:
		#0 == none
		#1 == 2 unsigned bytes
		#2 == 2 unsigned shorts
		#3 == 2 floats
		#colorType:
		#0-3 == none
		#4 == rgb565
		#5 == rgba5551
		#6 == rgba4444
		#7 == rgba8888
		#weightType:
		#0 == none
		#1 == unsigned byte * numWeights
		#2 == unsigned short * numWeights
		#3 == float * numWeights
		self.posType = vertexDict["posType"]
		self.posOfs = vertexDict["posOfs"]
		self.normalType = vertexDict["normalType"]
		self.normalOfs = vertexDict["normalOfs"]
		self.uvType = vertexDict["uvType"]
		self.uvOfs = vertexDict["uvOfs"]
		self.colorType = vertexDict["colorType"]
		self.colorOfs = vertexDict["colorOfs"]
		self.indexType = vertexDict["indexType"]
		self.weightOfs = 0 #will always be first, if there are weights
		self.weightType = vertexDict["weightType"]
		self.numWeights = vertexDict["numWeights"]
		self.numMorphs = vertexDict["numMorphs"]
		self.vertexSize = vertexDict["vertexSize"]

	#bindBuffers takes a chunk of data and binds buffers using the provided properties.
	#only call this function if there's an active rapi module instance.
	def bindBuffers(self, vertexData, bindWeights = True):
		rapi.rpgClearBufferBinds()
		if self.posType != 0:
			bindTypes = (0, noesis.RPGEODATA_BYTE, noesis.RPGEODATA_SHORT, noesis.RPGEODATA_FLOAT)
			rapi.rpgBindPositionBufferOfs(vertexData, bindTypes[self.posType], self.vertexSize, self.posOfs)
		if self.normalType != 0:
			bindTypes = (0, noesis.RPGEODATA_BYTE, noesis.RPGEODATA_SHORT, noesis.RPGEODATA_FLOAT)
			rapi.rpgBindNormalBufferOfs(vertexData, bindTypes[self.normalType], self.vertexSize, self.normalOfs)
		if self.uvType != 0:
			bindTypes = (0, noesis.RPGEODATA_UBYTE, noesis.RPGEODATA_USHORT, noesis.RPGEODATA_FLOAT)
			rapi.rpgBindUV1BufferOfs(vertexData, bindTypes[self.uvType], self.vertexSize, self.uvOfs)
		if self.colorType == 7:
			#binding is not natively supported for the other color formats. if you want to use them, you need to decode them before binding.
			rapi.rpgBindColorBufferOfs(vertexData, noesis.RPGEODATA_UBYTE, self.vertexSize, self.colorOfs, 4)
		if bindWeights is True and self.weightType != 0:
			bindTypes = (0, noesis.RPGEODATA_UBYTE, noesis.RPGEODATA_USHORT, noesis.RPGEODATA_FLOAT)
			rapi.rpgBindBoneWeightBufferOfs(vertexData, bindTypes[self.weightType], self.vertexSize, self.weightOfs, self.numWeights)


#random utility methods/classes

#convert a string to a padded bytearray
def noePadByteString(str, padLen):
	bstr = bytearray(str, "ASCII")
	if len(bstr) >= padLen: #check is >= under the expectation that the string should be 0-terminated
		noesis.doException("Provided string exceeds max length")
	exLen = padLen-len(bstr)
	bstr.extend(0 for i in range(0, exLen)) #pad out
	return bstr


#shortcut to get superclass
def noeSuper(clobj):
	return super(clobj.__class__, clobj)


#converts a list into bytes (providing items in list support toBytes)
def noeListBytes(lobj):
	b = bytes()
	for li in lobj:
		b += li.toBytes()
	return b


#converts a single-dimension tuple to a list
def noeTupleToList(tup):
	return [item for item in tup]


#converts bytes to string assuming standard ascii encoding
def noeStrFromBytes(bar, enc = "ASCII"):
	return str(bar, enc).rstrip("\0")

	
#force filtering to ascii range
def noeAsciiFromBytes(bar):
	filtered = bytearray([x if x < 0x80 else 0x2D for x in bar])
	return str(filtered, "ASCII").rstrip("\0")


#construct a bytearray containing the contents of data up to the first 0
def noeParseToZero(data):
	dst = bytearray()
	for c in data:
		if c == 0:
			break
		dst += noePack("B", c)
	return dst


#pad a bytearray out to a given alignment (assumes power of 2 alignment)
def noePaddedByteArray(data, alignment):
	alignmentMinusOne = alignment - 1
	r = len(data) & alignmentMinusOne
	if r != 0:
		return data + bytearray(alignment - r)
	return data
	

#returns None if the object doesn't have the given attribute, otherwise returns the attribute
def noeSafeGet(obj, attr):
	if hasattr(obj, attr):
		return getattr(obj, attr)
	return None


#returns a c-array style float representation of a list in a string
def noeCFloatRepr(obj):
	str = "{ "
	for i in range(0, len(obj)):
		if i > 0:
			str += ", "
		str += repr(obj[i])
		str += "f"
	return str + " }"


#turns print-style args list into a string
def noeStringizeObjects(*args):
	return " ".join(map(str, args))


def noeCmpToKey(cmpMethod):
	class KeyClassImpl:
		def __init__(self, obj, *args):
			self.obj = obj
		def __lt__(self, other):
			return cmpMethod(self.obj, other.obj) < 0
		def __gt__(self, other):
			return cmpMethod(self.obj, other.obj) > 0
		def __eq__(self, other):
			return cmpMethod(self.obj, other.obj) == 0
		def __le__(self, other):
			return cmpMethod(self.obj, other.obj) <= 0
		def __ge__(self, other):
			return cmpMethod(self.obj, other.obj) >= 0
		def __ne__(self, other):
			return cmpMethod(self.obj, other.obj) != 0
	return KeyClassImpl

	
def noeDefaultCertPath():
	return noesis.getScenesPath() + "defaultcert.pem"
	

#can be referenced to bypass data format checks (not recommended if it's possible to identify a format by its raw content)
def noeCheckGeneric(data):
	return 1


#pixelImageInfo should be a list of faceCount, mipCount, faceSize (total size of all mips for 1 face), mipsInfo
#mipsInfo is then a list of tuples in the form of (mipWidth, mipHeight, mipOffset, mipSize)
def noeProcessImage(data, pixelImageInfo, processFunction, *processFunctionArgs):
	faceCount, mipCount, mipsTotalSize, mipInfo = pixelImageInfo
	if faceCount <= 0:
		print("WARNING: noeProcessImage assuming at least 1 face.")
		faceCount = 1
	if mipCount <= 0:
		print("WARNING: noeProcessImage assuming at least 1 mip.")
		mipCount = 1
	
	if mipCount > len(mipInfo):
		print("ERROR: Not enough mipInfo to cover mip count.")
		return data
	
	#we want to process mip levels from large to small, so sort mip infos by size first
	sortedMipInfo = sorted(mipInfo, key = lambda mi: mi[0]*mi[1], reverse = True)
	
	dataOfs = 0
	processedData = bytearray()
	newMipsTotalSize = 0
	newMipsInfo = []
	for faceIndex in range(0, faceCount):
		processedMips = bytearray()
		for mipIndex in range(0, mipCount):
			mipW, mipH, mipOfs, mipSize = sortedMipInfo[mipIndex]
			processedMip = processFunction(data[dataOfs+mipOfs:dataOfs+mipOfs+mipSize], mipW, mipH, *processFunctionArgs)

			if faceIndex == 0:
				#fill in mip info if we're on the first face
				newMipsInfoEntry = (mipW, mipH, len(processedMips), len(processedMip))
				newMipsInfo.append(newMipsInfoEntry)
				newMipsTotalSize += len(processedMip)
				
			processedMips += processedMip
		dataOfs += mipsTotalSize
		processedData += processedMips
	
	#put the data back in the info list, overriding mip offsets/sizes with our new processed offsets/sizes
	pixelImageInfo[:] = [faceCount, mipCount, newMipsTotalSize, newMipsInfo]
	return processedData


#--------------------------------------------------------------------------------------------
#methods/classes beyond this point should not be referenced when the rapi-state is not valid.
#doing so will trigger a Python runtime exception.
#(rapi methods may create/reference per-instance pool allocation data, while noesis methods
#are guaranteed to work across instances)
#--------------------------------------------------------------------------------------------

#converts a list of NoeVertWeight objects into a flat list
class NoeFlatWeights:
	def __init__(self, vwList):
		self.numWeights = len(vwList)
		self.flatW = rapi.getFlatWeights(vwList, 0)
		self.weightValOfs = len(self.flatW) // 2
		self.weightsPerVert = (self.weightValOfs // 4) // self.numWeights
