import 'package:equatable/equatable.dart';

class Client extends Equatable {
  final String id;
  final String firstName;
  final String lastName;
  final String email;
  final String? phone;
  final String? objectives;
  final String? notes;
  final DateTime createdAt;

  const Client({
    required this.id,
    required this.firstName,
    required this.lastName,
    required this.email,
    this.phone,
    this.objectives,
    this.notes,
    required this.createdAt,
  });

  String get fullName => '$firstName $lastName';
  String get initials => '${firstName.isNotEmpty ? firstName[0] : ''}${lastName.isNotEmpty ? lastName[0] : ''}'.toUpperCase();

  factory Client.fromJson(Map<String, dynamic> json) => Client(
        id: json['id'] as String,
        firstName: json['first_name'] as String,
        lastName: json['last_name'] as String,
        email: json['email'] as String,
        phone: json['phone'] as String?,
        objectives: json['objectives'] as String?,
        notes: json['notes'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'phone': phone,
        'objectives': objectives,
        'notes': notes,
      };

  @override
  List<Object?> get props => [id, firstName, lastName, email, phone, objectives, notes, createdAt];
}
