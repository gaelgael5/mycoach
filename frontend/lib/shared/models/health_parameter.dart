import 'package:equatable/equatable.dart';

/// Paramètre de santé disponible dans l'application.
class HealthParameter extends Equatable {
  const HealthParameter({
    required this.id,
    required this.slug,
    required this.label,
    required this.unit,
    required this.dataType,
    required this.category,
    required this.active,
    required this.position,
  });

  final String id;
  final String slug;

  /// Labels i18n : {"fr": "Poids", "en": "Weight"}
  final Map<String, String> label;

  /// Unité de mesure : "kg", "bpm", "%", etc.
  final String unit;

  /// Type de donnée : "decimal", "integer", "percentage"
  final String dataType;

  final String category;
  final bool active;
  final int position;

  /// Retourne le label pour la locale donnée (fallback sur "fr" puis première valeur).
  String labelFor(String locale) {
    return label[locale] ??
        label['fr'] ??
        label.values.firstOrNull ??
        slug;
  }

  factory HealthParameter.fromJson(Map<String, dynamic> json) {
    final rawLabel = json['label'];
    Map<String, String> parsedLabel;
    if (rawLabel is Map) {
      parsedLabel = rawLabel.map(
        (k, v) => MapEntry(k.toString(), v.toString()),
      );
    } else {
      parsedLabel = {'fr': rawLabel?.toString() ?? '', 'en': rawLabel?.toString() ?? ''};
    }
    return HealthParameter(
      id:       json['id'] as String,
      slug:     json['slug'] as String,
      label:    parsedLabel,
      unit:     json['unit'] as String? ?? '',
      dataType: json['data_type'] as String? ?? 'decimal',
      category: json['category'] as String? ?? 'general',
      active:   json['active'] as bool? ?? true,
      position: json['position'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
    'id':        id,
    'slug':      slug,
    'label':     label,
    'unit':      unit,
    'data_type': dataType,
    'category':  category,
    'active':    active,
    'position':  position,
  };

  @override
  List<Object?> get props => [id, slug, unit, dataType, category, active, position];
}
