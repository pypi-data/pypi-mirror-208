/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Enum Utility Definitions                                                   *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace acc {
::llvm::StringRef stringifyClauseDefaultValue(ClauseDefaultValue val) {
  switch (val) {
    case ClauseDefaultValue::Present: return "present";
    case ClauseDefaultValue::None: return "none";
  }
  return "";
}

::std::optional<ClauseDefaultValue> symbolizeClauseDefaultValue(::llvm::StringRef str) {
  return ::llvm::StringSwitch<::std::optional<ClauseDefaultValue>>(str)
      .Case("present", ClauseDefaultValue::Present)
      .Case("none", ClauseDefaultValue::None)
      .Default(::std::nullopt);
}
::std::optional<ClauseDefaultValue> symbolizeClauseDefaultValue(uint32_t value) {
  switch (value) {
  case 0: return ClauseDefaultValue::Present;
  case 1: return ClauseDefaultValue::None;
  default: return ::std::nullopt;
  }
}

} // namespace acc
} // namespace mlir

namespace mlir {
namespace acc {
::llvm::StringRef stringifyDataClause(DataClause val) {
  switch (val) {
    case DataClause::acc_copyin: return "acc_copyin";
    case DataClause::acc_copyin_readonly: return "acc_copyin_readonly";
    case DataClause::acc_copy: return "acc_copy";
    case DataClause::acc_copyout: return "acc_copyout";
    case DataClause::acc_copyout_zero: return "acc_copyout_zero";
    case DataClause::acc_present: return "acc_present";
    case DataClause::acc_create: return "acc_create";
    case DataClause::acc_create_zero: return "acc_create_zero";
    case DataClause::acc_delete: return "acc_delete";
    case DataClause::acc_attach: return "acc_attach";
    case DataClause::acc_detach: return "acc_detach";
    case DataClause::acc_no_create: return "acc_no_create";
    case DataClause::acc_private: return "acc_private";
    case DataClause::acc_firstprivate: return "acc_firstprivate";
    case DataClause::acc_deviceptr: return "acc_deviceptr";
    case DataClause::acc_getdeviceptr: return "acc_getdeviceptr";
    case DataClause::acc_update_host: return "acc_update_host";
    case DataClause::acc_update_self: return "acc_update_self";
    case DataClause::acc_update_device: return "acc_update_device";
    case DataClause::acc_use_device: return "acc_use_device";
  }
  return "";
}

::std::optional<DataClause> symbolizeDataClause(::llvm::StringRef str) {
  return ::llvm::StringSwitch<::std::optional<DataClause>>(str)
      .Case("acc_copyin", DataClause::acc_copyin)
      .Case("acc_copyin_readonly", DataClause::acc_copyin_readonly)
      .Case("acc_copy", DataClause::acc_copy)
      .Case("acc_copyout", DataClause::acc_copyout)
      .Case("acc_copyout_zero", DataClause::acc_copyout_zero)
      .Case("acc_present", DataClause::acc_present)
      .Case("acc_create", DataClause::acc_create)
      .Case("acc_create_zero", DataClause::acc_create_zero)
      .Case("acc_delete", DataClause::acc_delete)
      .Case("acc_attach", DataClause::acc_attach)
      .Case("acc_detach", DataClause::acc_detach)
      .Case("acc_no_create", DataClause::acc_no_create)
      .Case("acc_private", DataClause::acc_private)
      .Case("acc_firstprivate", DataClause::acc_firstprivate)
      .Case("acc_deviceptr", DataClause::acc_deviceptr)
      .Case("acc_getdeviceptr", DataClause::acc_getdeviceptr)
      .Case("acc_update_host", DataClause::acc_update_host)
      .Case("acc_update_self", DataClause::acc_update_self)
      .Case("acc_update_device", DataClause::acc_update_device)
      .Case("acc_use_device", DataClause::acc_use_device)
      .Default(::std::nullopt);
}
::std::optional<DataClause> symbolizeDataClause(uint64_t value) {
  switch (value) {
  case 1: return DataClause::acc_copyin;
  case 2: return DataClause::acc_copyin_readonly;
  case 3: return DataClause::acc_copy;
  case 4: return DataClause::acc_copyout;
  case 5: return DataClause::acc_copyout_zero;
  case 6: return DataClause::acc_present;
  case 7: return DataClause::acc_create;
  case 8: return DataClause::acc_create_zero;
  case 9: return DataClause::acc_delete;
  case 10: return DataClause::acc_attach;
  case 11: return DataClause::acc_detach;
  case 12: return DataClause::acc_no_create;
  case 13: return DataClause::acc_private;
  case 14: return DataClause::acc_firstprivate;
  case 15: return DataClause::acc_deviceptr;
  case 16: return DataClause::acc_getdeviceptr;
  case 17: return DataClause::acc_update_host;
  case 18: return DataClause::acc_update_self;
  case 19: return DataClause::acc_update_device;
  case 20: return DataClause::acc_use_device;
  default: return ::std::nullopt;
  }
}

bool DataClauseAttr::classof(::mlir::Attribute attr) {
  return (((::llvm::isa<::mlir::IntegerAttr>(attr))) && ((::llvm::cast<::mlir::IntegerAttr>(attr).getType().isSignlessInteger(64)))) && (((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 1)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 2)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 3)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 4)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 5)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 6)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 7)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 8)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 9)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 10)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 11)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 12)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 13)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 14)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 15)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 16)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 17)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 18)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 19)) || ((::llvm::cast<::mlir::IntegerAttr>(attr).getInt() == 20)));
}
DataClauseAttr DataClauseAttr::get(::mlir::MLIRContext *context, DataClause val) {
  ::mlir::IntegerType intType = ::mlir::IntegerType::get(context, 64);
  ::mlir::IntegerAttr baseAttr = ::mlir::IntegerAttr::get(intType, static_cast<uint64_t>(val));
  return baseAttr.cast<DataClauseAttr>();
}
DataClause DataClauseAttr::getValue() const {
  return static_cast<DataClause>(::mlir::IntegerAttr::getInt());
}
} // namespace acc
} // namespace mlir

namespace mlir {
namespace acc {
::llvm::StringRef stringifyReductionOp(ReductionOp val) {
  switch (val) {
    case ReductionOp::redop_add: return "redop_add";
    case ReductionOp::redop_mul: return "redop_mul";
    case ReductionOp::redop_max: return "redop_max";
    case ReductionOp::redop_min: return "redop_min";
    case ReductionOp::redop_and: return "redop_and";
    case ReductionOp::redop_or: return "redop_or";
    case ReductionOp::redop_xor: return "redop_xor";
    case ReductionOp::redop_leqv: return "redop_leqv";
    case ReductionOp::redop_lneqv: return "redop_lneqv";
    case ReductionOp::redop_land: return "redop_land";
    case ReductionOp::redop_lor: return "redop_lor";
  }
  return "";
}

::std::optional<ReductionOp> symbolizeReductionOp(::llvm::StringRef str) {
  return ::llvm::StringSwitch<::std::optional<ReductionOp>>(str)
      .Case("redop_add", ReductionOp::redop_add)
      .Case("redop_mul", ReductionOp::redop_mul)
      .Case("redop_max", ReductionOp::redop_max)
      .Case("redop_min", ReductionOp::redop_min)
      .Case("redop_and", ReductionOp::redop_and)
      .Case("redop_or", ReductionOp::redop_or)
      .Case("redop_xor", ReductionOp::redop_xor)
      .Case("redop_leqv", ReductionOp::redop_leqv)
      .Case("redop_lneqv", ReductionOp::redop_lneqv)
      .Case("redop_land", ReductionOp::redop_land)
      .Case("redop_lor", ReductionOp::redop_lor)
      .Default(::std::nullopt);
}
::std::optional<ReductionOp> symbolizeReductionOp(uint32_t value) {
  switch (value) {
  case 0: return ReductionOp::redop_add;
  case 1: return ReductionOp::redop_mul;
  case 2: return ReductionOp::redop_max;
  case 3: return ReductionOp::redop_min;
  case 4: return ReductionOp::redop_and;
  case 5: return ReductionOp::redop_or;
  case 6: return ReductionOp::redop_xor;
  case 7: return ReductionOp::redop_leqv;
  case 8: return ReductionOp::redop_lneqv;
  case 9: return ReductionOp::redop_land;
  case 10: return ReductionOp::redop_lor;
  default: return ::std::nullopt;
  }
}

} // namespace acc
} // namespace mlir

