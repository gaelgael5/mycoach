import 'package:equatable/equatable.dart';

/// Log d'un paramètre de santé enregistré par l'utilisateur.
class HealthLog extends Equatable {
  const HealthLog({
    required this.id,
    required this.parameterId,
    required this.parameterSlug,
    required this.parameterLabel,
    required this.value,
    required this.unit,
    required this.measuredAt,
  });

  final String id;
  final String parameterId;
  final String parameterSlug;
  final String parameterLabel;
  final double value;
  final String unit;
  final DateTime measuredAt;

  factory HealthLog.fromJson(Map<String, dynamic> json) => HealthLog(
    id:             json['id'] as String,
    parameterId:    json['parameter_id'] as String,
    parameterSlug:  json['parameter_slug'] as String? ?? '',
    parameterLabel: json['parameter_label'] as String? ?? '',
    value:          (json['value'] as num).toDouble(),
    unit:           json['unit'] as String? ?? '',
    measuredAt:     DateTime.parse(json['measured_at'] as String),
  );

  Map<String, dynamic> toJson() => {
    'id':              id,
    'parameter_id':    parameterId,
    'parameter_slug':  parameterSlug,
    'parameter_label': parameterLabel,
    'value':           value,
    'unit':            unit,
    'measured_at':     measuredAt.toIso8601String(),
  };

  @override
  List<Object?> get props =>
      [id, parameterId, parameterSlug, value, unit, measuredAt];
}
