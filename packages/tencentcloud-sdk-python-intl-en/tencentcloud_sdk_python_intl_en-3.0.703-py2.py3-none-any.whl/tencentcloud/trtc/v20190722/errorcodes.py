# -*- coding: utf8 -*-
# Copyright (c) 2017-2021 THL A29 Limited, a Tencent company. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# CAM signature/authentication error.
AUTHFAILURE = 'AuthFailure'

# Identity verification has not been completed, so this operation is not allowed.
AUTHFAILURE_UNREALNAMEAUTHENTICATED = 'AuthFailure.UnRealNameAuthenticated'

# CAM authentication failed.
AUTHFAILURE_UNAUTHORIZEDOPERATION = 'AuthFailure.UnauthorizedOperation'

# Unsupported operation.
AUTHFAILURE_UNSUPPORTEDOPERATION = 'AuthFailure.UnsupportedOperation'

# Operation failed.
FAILEDOPERATION = 'FailedOperation'

# Unsupported on-cloud recording method.
FAILEDOPERATION_CRUNSUPPORTMETHOD = 'FailedOperation.CRUnsupportMethod'

# Maximum number of concurrent on-cloud recording tasks reached. Contact us to raise the limit.
FAILEDOPERATION_RESTRICTEDCONCURRENCY = 'FailedOperation.RestrictedConcurrency'

# The room does not exist.
FAILEDOPERATION_ROOMNOTEXIST = 'FailedOperation.RoomNotExist'

# The application ID does not exist.
FAILEDOPERATION_SDKAPPIDNOTEXIST = 'FailedOperation.SdkAppIdNotExist'

# The user is not in the room.
FAILEDOPERATION_USERNOTEXIST = 'FailedOperation.UserNotExist'

# Internal error.
INTERNALERROR = 'InternalError'

# On-cloud recording internal error.
INTERNALERROR_CRINTERNALERROR = 'InternalError.CRInternalError'

# An error occurred while querying the database.
INTERNALERROR_DBERROR = 'InternalError.DBError'

# Failed to query the room.
INTERNALERROR_GETROOMCACHEIPERROR = 'InternalError.GetRoomCacheIpError'

# Failed to get room information.
INTERNALERROR_GETROOMFROMCACHEERROR = 'InternalError.GetRoomFromCacheError'

# The user is not in the room.
INTERNALERROR_USERNOTEXIST = 'InternalError.UserNotExist'

# Parameter error.
INVALIDPARAMETER = 'InvalidParameter'

# Parameter value is out of range.
INVALIDPARAMETER_OUTOFRANGE = 'InvalidParameter.OutOfRange'

# The query period exceeds the limit.
INVALIDPARAMETER_QUERYSCALEOVERSIZE = 'InvalidParameter.QueryScaleOversize'

# `RoomId` is incorrect.
INVALIDPARAMETER_ROOMID = 'InvalidParameter.RoomId'

# `SdkAppId` is incorrect.
INVALIDPARAMETER_SDKAPPID = 'InvalidParameter.SdkAppId'

# Invalid `UserId`.
INVALIDPARAMETER_USERID = 'InvalidParameter.UserId'

# `UserIds` is incorrect.
INVALIDPARAMETER_USERIDS = 'InvalidParameter.UserIds'

# Invalid RoomId.
INVALIDPARAMETERVALUE_ROOMID = 'InvalidParameterValue.RoomId'

# Missing parameter.
MISSINGPARAMETER = 'MissingParameter'

# `AccessKey` parameter missing.
MISSINGPARAMETER_ACCESSKEY = 'MissingParameter.AccessKey'

# `AppId` missing.
MISSINGPARAMETER_APPID = 'MissingParameter.AppId'

# `Bucket` parameter missing.
MISSINGPARAMETER_BUCKET = 'MissingParameter.Bucket'

# `CloudStorage` parameter missing.
MISSINGPARAMETER_CLOUDSTORAGE = 'MissingParameter.CloudStorage'

# `RecordMode` parameter missing.
MISSINGPARAMETER_RECORDMODE = 'MissingParameter.RecordMode'

# `RecordParams` parameter missing.
MISSINGPARAMETER_RECORDPARAMS = 'MissingParameter.RecordParams'

# `Region` parameter missing.
MISSINGPARAMETER_REGION = 'MissingParameter.Region'

# `RoomId` is missing.
MISSINGPARAMETER_ROOMID = 'MissingParameter.RoomId'

# `SdkAppId` is missing.
MISSINGPARAMETER_SDKAPPID = 'MissingParameter.SdkAppId'

# `SecretKey` parameter missing.
MISSINGPARAMETER_SECRETKEY = 'MissingParameter.SecretKey'

# `StorageParams` parameter missing.
MISSINGPARAMETER_STORAGEPARAMS = 'MissingParameter.StorageParams'

# `StreamType` parameter missing.
MISSINGPARAMETER_STREAMTYPE = 'MissingParameter.StreamType'

# `TaskId` parameter missing.
MISSINGPARAMETER_TASKID = 'MissingParameter.TaskId'

# Missing `UserId` parameter.
MISSINGPARAMETER_USERID = 'MissingParameter.UserId'

# `UserIds` is missing.
MISSINGPARAMETER_USERIDS = 'MissingParameter.UserIds'

# `UserSig` parameter missing.
MISSINGPARAMETER_USERSIG = 'MissingParameter.UserSig'

# `Vendor` parameter missing.
MISSINGPARAMETER_VENDOR = 'MissingParameter.Vendor'

# The resource does not exist.
RESOURCENOTFOUND = 'ResourceNotFound'

# No permission to manipulate `SdkAppId`.
UNAUTHORIZEDOPERATION_SDKAPPID = 'UnauthorizedOperation.SdkAppId'

# Unsupported operation.
UNSUPPORTEDOPERATION = 'UnsupportedOperation'
