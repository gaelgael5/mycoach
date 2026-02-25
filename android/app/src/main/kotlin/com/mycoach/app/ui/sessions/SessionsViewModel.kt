package com.mycoach.app.ui.sessions

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mycoach.app.api.ApiClient
import com.mycoach.app.models.Session
import com.mycoach.app.models.SessionRequest
import kotlinx.coroutines.launch

class SessionsViewModel : ViewModel() {

    private val _sessions = MutableLiveData<List<Session>>()
    val sessions: LiveData<List<Session>> = _sessions

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _loading = MutableLiveData(false)
    val loading: LiveData<Boolean> = _loading

    fun load(clientId: Int? = null) {
        viewModelScope.launch {
            _loading.value = true
            try {
                _sessions.value = ApiClient.service.getSessions(clientId)
                _error.value = null
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _loading.value = false
            }
        }
    }

    fun create(request: SessionRequest) {
        viewModelScope.launch {
            try {
                ApiClient.service.createSession(request)
                load()
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun delete(id: Int) {
        viewModelScope.launch {
            try {
                ApiClient.service.deleteSession(id)
                load()
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
}
