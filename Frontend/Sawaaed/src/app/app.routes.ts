import { Routes } from '@angular/router';
import { LoginComponent } from './main/auth/login/login.component';
import { PublisherComponent } from './main/publisher/publisher.component';
import { SubscriberComponent } from './main/subscriber/subscriber.component';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    { path: 'publisher', component: PublisherComponent },
    { path: 'subscriber', component: SubscriberComponent},
    { path: '', redirectTo: 'login', pathMatch: 'full' }

];
