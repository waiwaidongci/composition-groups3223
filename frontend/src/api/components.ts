import {request} from './client';import {Component} from '../types/domain';export const getComponents=(id:number)=>request<Component[]>(`/studies/${id}/components`);
