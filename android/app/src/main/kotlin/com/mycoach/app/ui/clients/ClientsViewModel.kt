package com.mycoach.app.ui.clients

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mycoach.app.api.ApiClient
import com.mycoach.app.models.Client
import com.mycoach.app.models.ClientRequest
import kotlinx.coroutines.launch

class ClientsViewModel : ViewModel() {

    private val _clients = MutableLiveData<List<Client>>()
    val clients: LiveData<List<Client>> = _clients

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private val _loading = MutableLiveData(false)
    val loading: LiveData<Boolean> = _loading

    private val _saved = MutableLiveData<Boolean>()
    val saved: LiveData<Boolean> = _saved

    fun load() {
        viewModelScope.launch {
            _loading.value = true
            try {
                _clients.value = ApiClient.service.getClients()
                _error.value = null
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _loading.value = false
            }
        }
    }

    fun save(id: Int?, request: ClientRequest) {
        viewModelScope.launch {
            try {
                if (id != null) ApiClient.service.updateClient(id, request)
                else ApiClient.service.createClient(request)
                _saved.value = true
                load()
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun delete(id: Int) {
        viewModelScope.launch {
            try {
                ApiClient.service.deleteClient(id)
                load()
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
}
